class BASE_TOK():
    def __init__(self):
        self.value = ""
        
class INT_TOK(BASE_TOK):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return "INT_TOK"

class ADD_TOK(BASE_TOK):
    def __init__(self):
        self.value = "+"

    def __repr__(self):
        return "ADD_TOK"

class MUL_TOK(BASE_TOK):
    def __init__(self):
        self.value = "*"

    def __repr__(self):
        return "MUL_TOK"

class LEFT_PAREN_TOK(BASE_TOK):
    def __init__(self):
        self.value = "("

    def __repr__(self):
        return "LEFT_PAREN_TOK"
    
class RIGHT_PAREN_TOK(BASE_TOK):
    def __init__(self):
        self.value = ")"

    def __repr__(self):
        return "RIGHT_PAREN_TOK"
    
class SPACE_TOK(BASE_TOK):
    def __init__(self):
        self.value = " "

    def __repr__(self):
        return "SPACE_TOK"
    
class EOS_TOK(BASE_TOK):
    def __repr__(self):
        return "EOS_TOK"