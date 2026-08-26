from app.validators.contact_validator import ContactValidator

def test_email_invalide_rejete():
    validator = ContactValidator()
    assert validator.is_valid_email("pas-un-email") is False

def test_email_valide_accepte():
    validator = ContactValidator()
    assert validator.is_valid_email("contact@acme.com") is True

def test_whatsapp_avec_espaces_normalise():
    validator = ContactValidator()
    assert validator.is_valid_whatsapp("+237 677 123 456") is True

def test_validate_prospect_contact_sans_canal():
    validator = ContactValidator()
    erreur = validator.validate_prospect_contact("ACME", None, None)
    assert erreur is not None

def test_validate_prospect_contact_avec_email_valide():
    validator = ContactValidator()
    erreur = validator.validate_prospect_contact("ACME", "contact@acme.com", None)
    assert erreur is None