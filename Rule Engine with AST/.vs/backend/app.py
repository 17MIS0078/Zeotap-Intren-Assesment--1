from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

class Node:
    def __init__(self, node_type, value):
        self.node_type = node_type  # 'operand' or 'operator'
        self.value = value
        self.left = None
        self.right = None

def parse_condition(condition):
    parts = condition.split()
    if len(parts) != 3:
        raise ValueError("Invalid condition format. Use 'attribute operator value'")
    
    attr, operator, value = parts[0], parts[1], parts[2].strip("'")  # Stripping any quotes
    # Convert numeric values to int if applicable
    try:
        value = int(value)
    except ValueError:
        pass  # Keep as string if conversion fails
    
    return attr, operator, value

def create_rule(rule_string):
    root = None

    # Split by 'OR' first
    or_conditions = [condition.strip() for condition in rule_string.split('OR')]
    for or_condition in or_conditions:
        if root is None:
            root = Node("operator", "OR")
            root.left = create_rule_for_and_conditions(or_condition)
        else:
            new_node = Node("operator", "OR")
            new_node.left = root
            new_node.right = create_rule_for_and_conditions(or_condition)
            root = new_node
            
    return root

def create_rule_for_and_conditions(and_condition_string):
    root = None
    conditions = [condition.strip() for condition in and_condition_string.split('AND')]
    
    for condition in conditions:
        if root is None:
            root = Node("operand", condition)
        else:
            new_node = Node("operator", "AND")
            new_node.left = root
            new_node.right = Node("operand", condition)
            root = new_node
            
    return root

def evaluate_rule(node, user_data):
    if node is None:
        return False

    if node.node_type == "operand":
        attr, operator, value = parse_condition(node.value)
        
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json

    # Log the incoming request data
    print("Received data:", data)

    rule = data.get('rule', '')
    user_data = data.get('user_data', '{}')

    # Check if user_data is in string format and parse it
    if isinstance(user_data, str):
        try:
            user_data = json.loads(user_data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid user data format. Please provide valid JSON."}), 400

    # Log the parsed user_data for debugging
    print("Parsed user data:", user_data)

    try:
        rule_tree = create_rule(rule)
        is_eligible = evaluate_rule(rule_tree, user_data)
        return jsonify({"eligible": is_eligible})
    except Exception as e:
        print(f"Error while evaluating rule: {e}")  # Log the error for debugging
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
