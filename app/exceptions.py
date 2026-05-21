class ValidationError(Exception):
    pass

class NegativeAmountError(ValidationError):
    pass

class DuplicateRuleError(ValidationError):
    pass

class DuplicatePayslipError(ValidationError):
    pass