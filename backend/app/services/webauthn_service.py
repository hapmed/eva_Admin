"""Lógica de passkeys (WebAuthn) y nombres de dispositivo tipo Ubuntu.

Los nombres combinan un adjetivo y un animal (p. ej. «Brave Badger»), únicos por
usuario, para identificar el dispositivo de la passkey.
"""

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from app.core.auth import AuthContext
from app.core.webauthn import b64url_decode
from app.models.user import HapmedUser
from app.models.webauthn import WebAuthnCredential
from app.services import audit
from app.services.util import as_uuid

ADJECTIVES = [
    "Brave",
    "Calm",
    "Clever",
    "Cosmic",
    "Daring",
    "Eager",
    "Gentle",
    "Golden",
    "Happy",
    "Honest",
    "Jolly",
    "Keen",
    "Lively",
    "Lucky",
    "Mellow",
    "Merry",
    "Noble",
    "Nimble",
    "Playful",
    "Proud",
    "Quick",
    "Quiet",
    "Radiant",
    "Rapid",
    "Silent",
    "Sleek",
    "Sturdy",
    "Sunny",
    "Swift",
    "Vivid",
    "Wise",
    "Zesty",
]

ANIMALS = [
    "Antelope",
    "Badger",
    "Beaver",
    "Bison",
    "Cheetah",
    "Cobra",
    "Dolphin",
    "Eagle",
    "Falcon",
    "Ferret",
    "Fossa",
    "Fox",
    "Gecko",
    "Heron",
    "Husky",
    "Ibis",
    "Jaguar",
    "Koala",
    "Lemur",
    "Lynx",
    "Marmot",
    "Meerkat",
    "Ocelot",
    "Otter",
    "Owl",
    "Panda",
    "Pelican",
    "Quokka",
    "Raccoon",
    "Raven",
    "Tapir",
    "Walrus",
    "Weasel",
    "Wolf",
    "Wombat",
    "Yak",
]


def list_credentials(db: Session, user_id) -> list[WebAuthnCredential]:
    return list(
        db.scalars(
            select(WebAuthnCredential)
            .where(WebAuthnCredential.user_id == user_id)
            .order_by(WebAuthnCredential.created_at)
        ).all()
    )


def count_credentials(db: Session, user_id) -> int:
    return len(list_credentials(db, user_id))


def generate_name(db: Session, user_id) -> str:
    for _ in range(25):
        candidate = f"{secrets.choice(ADJECTIVES)} {secrets.choice(ANIMALS)}"
        exists = db.scalar(
            select(WebAuthnCredential).where(
                WebAuthnCredential.user_id == user_id,
                WebAuthnCredential.name == candidate,
            )
        )
        if not exists:
            return candidate
    return f"{secrets.choice(ADJECTIVES)} {secrets.choice(ANIMALS)} {secrets.randbelow(9000) + 1000}"


def register_begin(db: Session, user: HapmedUser, rp_id: str, rp_name: str):
    exclude = [
        PublicKeyCredentialDescriptor(id=credential.credential_id)
        for credential in list_credentials(db, user.id)
    ]
    return generate_registration_options(
        rp_id=rp_id,
        rp_name=rp_name,
        user_name=user.email,
        user_id=str(user.id).encode(),
        exclude_credentials=exclude,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
    )


def register_complete(
    db: Session,
    context: AuthContext,
    user: HapmedUser,
    credential: dict,
    challenge: bytes,
    rp_id: str,
    expected_origin: str,
    name: str | None,
) -> WebAuthnCredential:
    verified = verify_registration_response(
        credential=credential,
        expected_challenge=challenge,
        expected_rp_id=rp_id,
        expected_origin=expected_origin,
    )
    transports: list = []
    if isinstance(credential, dict):
        response = credential.get("response") or {}
        transports = response.get("transports") or []

    final_name = name.strip() if name and name.strip() else generate_name(db, user.id)
    row = WebAuthnCredential(
        user_id=user.id,
        credential_id=verified.credential_id,
        public_key=verified.credential_public_key,
        sign_count=verified.sign_count,
        transports=transports,
        aaguid=str(verified.aaguid) if verified.aaguid else "",
        name=final_name,
    )
    db.add(row)
    db.flush()
    audit.record(db, context, "webauthn.register", "webauthn_credential", row.id, name=final_name)
    db.commit()
    db.refresh(row)
    return row


def login_begin(db: Session, rp_id: str, email: str | None):
    allow: list[PublicKeyCredentialDescriptor] = []
    if email:
        user = db.scalar(select(HapmedUser).where(HapmedUser.email == email))
        if user is not None:
            allow = [
                PublicKeyCredentialDescriptor(id=credential.credential_id)
                for credential in list_credentials(db, user.id)
            ]
    return generate_authentication_options(
        rp_id=rp_id,
        allow_credentials=allow,
        user_verification=UserVerificationRequirement.PREFERRED,
    )


def login_complete(
    db: Session,
    credential: dict,
    challenge: bytes,
    rp_id: str,
    expected_origin: str,
) -> tuple[HapmedUser, WebAuthnCredential]:
    if not isinstance(credential, dict):
        raise ValueError("credencial inválida")
    raw_id = credential.get("id") or credential.get("rawId")
    if not raw_id:
        raise ValueError("credencial inválida")
    credential_id = b64url_decode(raw_id)
    row = db.scalar(select(WebAuthnCredential).where(WebAuthnCredential.credential_id == credential_id))
    if row is None:
        raise LookupError("passkey no registrada")
    user = db.get(HapmedUser, row.user_id)
    if user is None or not user.is_active:
        raise LookupError("usuario no válido")

    verified = verify_authentication_response(
        credential=credential,
        expected_challenge=challenge,
        expected_rp_id=rp_id,
        expected_origin=expected_origin,
        credential_public_key=row.public_key,
        credential_current_sign_count=row.sign_count,
    )
    row.sign_count = verified.new_sign_count
    row.last_used_at = datetime.now(UTC)
    db.commit()
    db.refresh(row)
    return user, row


def delete_credential(db: Session, context: AuthContext, user_id, credential_id: str) -> None:
    row = db.get(WebAuthnCredential, as_uuid(credential_id))
    if row is None or str(row.user_id) != str(user_id):
        raise LookupError("passkey no encontrada")
    audit.record(db, context, "webauthn.delete", "webauthn_credential", row.id, name=row.name)
    db.delete(row)
    db.commit()
