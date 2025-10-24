class Node:
    def __init__(self, value):
        self.value = value
        self.left: Node | None = None
        self.right: Node | None = None


class ExpressionTree:
    def __init__(self, expression: str):
        self.root = None
        self.expression = expression
        self.variables = set()

    def __parentesis_balance(self, expression=None):
        if expression is None:
            expression = self.expression
        balance = 0
        for char in expression:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
                if balance < 0:
                    return False
        return balance == 0

    def __operator_priority(self, operator):
        priority_map = {
            '↔': 1,  # Bicondicional (menor prioridad)
            '→': 2,  # Implicación
            '∨': 3,  # Disyunción (OR)
            '∧': 4,  # Conjunción (AND)
            '¬': 5  # Negación (mayor prioridad)
        }
        return priority_map.get(operator, 0)

    def evaluate(self, variables):
        if variables is None:
            variables = {}

        # Verificar que todas las variables necesarias estén presentes
        missing_vars = self.variables - set(variables.keys())
        if missing_vars:
            raise ValueError(f"Faltan variables: {missing_vars}")

        return self.__evaluate_node(self.root, variables)

    def __evaluate_node(self, node, variables):
        if node is None:
            return False

        # Si es una variable, devolver su valor
        if node.value in variables:
            return variables[node.value]

        # Si es un operador, evaluar según el tipo
        if node.value == '¬':
            # Negación: puede ser unaria izquierda o derecha
            if node.left:
                return not self.__evaluate_node(node.left, variables)
            else:
                return not self.__evaluate_node(node.right, variables)

        # Operadores binarios
        left_value = self.__evaluate_node(node.left, variables)
        right_value = self.__evaluate_node(node.right, variables)

        if node.value == '∧':
            return left_value and right_value
        elif node.value == '∨':
            return left_value or right_value
        elif node.value == '→':
            return not left_value or right_value  # p → q ≡ ¬p ∨ q
        elif node.value == '↔':
            return left_value == right_value  # p ↔ q ≡ (p → q) ∧ (q → p)

        return False

    def build_tree(self):
        if not self.__parentesis_balance():
            raise ValueError("Expresión con paréntesis no balanceados")

        self.variables.clear()  # Limpiar variables previas
        self.root = self.__build_tree(self.expression.replace(" ", ""))

    def __build_tree(self, expression):
        # Eliminar paréntesis exteriores redundantes
        while (len(expression) > 0 and
               expression[0] == '(' and
               expression[-1] == ')' and
               self.__parentesis_balance(expression[1:-1])):
            expression = expression[1:-1]

        if not expression:
            return None

        # Buscar el operador de menor prioridad fuera de paréntesis
        min_priority = float('inf')
        index = -1
        level = 0

        # Recorrer de derecha a izquierda para operadores de igual prioridad
        for i in range(len(expression) - 1, -1, -1):
            char = expression[i]

            if char == ')':
                level += 1
            elif char == '(':
                level -= 1
            elif level == 0 and char in ['↔', '→', '∨', '∧', '¬']:
                priority = self.__operator_priority(char)
                if priority < min_priority:
                    min_priority = priority
                    index = i

        # Si no se encontró operador, debe ser una variable
        if index == -1:
            if len(expression) == 1 and expression.isalpha():
                self.variables.add(expression)
                return Node(expression)
            else:
                raise ValueError(f"Expresión no válida: '{expression}'")

        op = expression[index]

        # Manejar operador unario ¬
        if op == '¬':
            # Verificar si es un NOT al inicio
            if index == 0:
                right = self.__build_tree(expression[index + 1:])
                node = Node(op)
                node.right = right
                return node
            else:
                # Si no está al inicio, podría ser parte de una expresión más compleja
                # Continuar buscando otros operadores
                for i in range(len(expression) - 1, -1, -1):
                    if i == index:
                        continue
                    char = expression[i]
                    if char in ['↔', '→', '∨', '∧'] and self.__check_operator_level(expression, i) == 0:
                        priority = self.__operator_priority(char)
                        if priority < min_priority:
                            min_priority = priority
                            index = i
                            op = char
                            break

                if op == '¬':  # Si sigue siendo NOT
                    right = self.__build_tree(expression[index + 1:])
                    node = Node(op)
                    node.right = right
                    return node

        # Operadores binarios
        left = self.__build_tree(expression[:index])
        right = self.__build_tree(expression[index + 1:])
        node = Node(op)
        node.left = left
        node.right = right
        return node

    def __check_operator_level(self, expression, index):
        level = 0
        for i in range(index):
            if expression[i] == '(':
                level += 1
            elif expression[i] == ')':
                level -= 1
        return level

    def inorder_expression(self, node=None):
        if node is None:
            node = self.root
        if node is None:
            return ""

        # Si es una hoja (variable)
        if node.left is None and node.right is None:
            return str(node.value)

        # Si es negación
        if node.value == '¬':
            if node.right:
                return f"¬{self.inorder_expression(node.right)}"
            else:
                return f"¬{self.inorder_expression(node.left)}"

        # Operadores binarios
        left_expr = self.inorder_expression(node.left)
        right_expr = self.inorder_expression(node.right)
        return f"({left_expr} {node.value} {right_expr})"

    def get_variables(self):
        return self.variables.copy()

    def __str__(self):
        return f"ExpressionTree: {self.inorder_expression()}"