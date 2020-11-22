class SettingsError(RuntimeError):
    pass

class UndefinedSettingError(SettingsError):
    """
    Error thrown when trying to read a setting which was never set
    """
    pass

class UndefinedRequiredSettingError(UndefinedSettingError):
    """
    A setting marked as required is undefined when the settings were
    being validated.
    """
    pass

class NoSuchSettingError(AttributeError,SettingsError):
    """
    Error thrown when there is no setting with that name
    """
    pass

class NoSettingToUpdateError(NoSuchSettingError):
    """
    Error thrown when trying to update a setting that does not exist.
    """
    pass

class SettingsMapNotUpdatableError(NoSuchSettingError):
    """
    Error when trying to update a SettingsMap as if it were a setting.
    """
    pass

class SettingAlreadyExistsError(SettingsError):
    """
    Error thrown when trying to create a new setting where one already
    exists.
    """
    pass

class InvalidBulkAssignment(SettingsError):
    """
    Thrown when trying to bulk assign to a settingsmap in some invalid way.
    """
    pass

class InvalidSettingError(SettingsError):
    """
    Setting failed validation
    """
    pass

class SettingNotDerivableError(SettingsError):
    """
    Tried to derive setting with no derivation provided.
    """
    pass
