class Node:
    def __init__(self, node_type, value=None):
        self.node_type = node_type  # "operator" (AND/OR) or "operand" (conditions)
        self.left = None  # Left child node (for operators)
        self.right = None  # Right child node (for operators)
        self.value = value  # Value of operand nodes

def parse_condition(condition):
    parts = condition.split()
    if len(parts) != 3:
        raise ValueError("Invalid condition format")
    
    attr, operator, value = parts[0], parts[1], parts[2].strip("'")
    
    # Convert numeric values to int
    if value.isdigit():
        value = int(value)  
    return attr, operator, value

def evaluate_rule(node, user_data):
    if node.node_type == "operand":
        attr, operator, value = parse_condition(node.value)
        
        # Check if the attribute exists in user_data
        if attr not in user_data:
            print(f"Warning: Missing user data for attribute: {attr}. Evaluating as False.")
            return False
        
        # Evaluate based on the operator
        if operator == ">":
            return user_data[attr] > value
        elif operator == "<":
            return user_data[attr] < value
        elif operator == "=":
            return user_data[attr] == value
        elif operator == ">=":
            return user_data[attr] >= value
        elif operator == "<=":
            return user_data[attr] <= value
            
    elif node.node_type == "operator":
        left_eval = evaluate_rule(node.left, user_data)
        right_eval = evaluate_rule(node.right, user_data)
        
        if node.value == "AND":
            return left_eval and right_eval
        elif node.value == "OR":
            return left_eval or right_eval
            
    return False

def create_rule(rule_string):
    # Split the rule_string to create a simple tree structure
    parts = rule_string.split(" AND ")
    root = Node("operator", "AND")
    
    if len(parts) == 2:
        root.left = Node("operand", parts[0].strip())
        root.right = Node("operand", parts[1].strip())
    else:
        root.left = Node("operand", parts[0].strip())
    
    return root

# Example usage
if __name__ == "__main__":
    # Define a sample user data dictionary
    user_data = {
        "age": 25,
        "income": 35000
    }

    # Get the rule from the user
    rule_input = "age >= 18 AND income >= 30000"  
    rule = create_rule(rule_input)

    # Evaluate the rule against user data
    result = evaluate_rule(rule, user_data)
    print("Eligible:", result)
