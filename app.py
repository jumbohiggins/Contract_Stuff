from flask import Flask, render_template, request, redirect, jsonify, flash, url_for, os

app = Flask(__name__)

app.secret_key = 'Contract_Tools'

# Example user data structure
user_data = {
    "User1": {"username": "Buster", "funbucks": 100, "powers": {"Innate": 0, "Artifact": 0, "Consumable": 0, "Legendary": 0}, "bets": []},
    "User2": {"username": "Gob", "funbucks": 100, "powers": {"Innate": 0, "Artifact": 0, "Consumable": 0, "Legendary": 0}, "bets": []},
    "User3": {"username": "Maybe", "funbucks": 100, "powers": {"Innate": 0, "Artifact": 0, "Consumable": 0, "Legendary": 0}, "bets": []},
}

bonuses = {
        'Innate': sum(user['powers']['Innate'] for user in user_data.values()),
        'Artifact': sum(user['powers']['Artifact'] for user in user_data.values()),
        'Consumable': sum(user['powers']['Consumable'] for user in user_data.values()),
        'Legendary': sum(user['powers']['Legendary'] for user in user_data.values())
    }

user_colors = {
    'User1': 'lightblue',
    'User2': 'lightgreen',
    'User3': 'lightcoral',
    # Add more users and colors as needed
}

def get_power_display(power_value):
    if 0 <= power_value <= 2:
        return ""
    elif 3 <= power_value <= 4:
        return "+"
    elif 5 <= power_value <= 6:
        return "+2"
    else:
        return "+3"

def calculate_bonus(power_value):
    print(power_value)
    """ Calculate bonus based on power value. """
    if power_value >= 0 and power_value <= 2:
        return 0
    elif power_value >= 3 and power_value <= 4:
        return 1
    elif power_value >= 5 and power_value <= 6:
        return 2
    elif power_value < 0:
        return 0
    else:
        return 3


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Set names for each user
        user = request.form['user']
        user_value = request.form['user_value']  # Get the user data here
        power = request.form['power']

        for user in user_data.keys():
            username = request.form.get(f'user_name_{user}', user_data[user]['username'])
            user_data[user]['username'] = username  # Update the user's username

        # Handle power activation logic (if submitted)
        user = request.form['user']
        power = request.form['power']

        # Your existing power activation logic goes here...
        for user, data in user_data.items():
            data['power_display'] = get_power_display(data['power_value'])

    print("FSDasdf")
    return render_template('index.html', user_data=user_data, user_colors=user_colors, bonuses=bonuses)

@app.route('/reduce_powers', methods=['POST'])
def reduce_powers():
    # Adjust power activation values towards 0
    for user, data in user_data.items():
        for power, value in data["powers"].items():
            if value > 0:
                data["powers"][power] = value - 1  # Decrease positive values
            elif value < 0:
                data["powers"][power] = value + 1  # Increase negative values
    return redirect(url_for('index'))  # Redirect back to the main page or wherever you need


@app.route('/update_username', methods=['POST'])
def update_username():
    user = request.form.get('user')  # Get which user to update
    new_username = request.form.get('username')  # Get the new username

    # Update the username in user_data
    if user in user_data:
        user_data[user]['username'] = new_username

    return redirect(url_for('index'))  # Redirect to the main page


@app.route('/update_power', methods=['POST'])
def update_power():
    user_id = request.form.get('user_id')  # e.g., 'User1', 'User2', etc.
    power_type = request.form.get('power_type')  # e.g., 'Innate', 'Artifact', etc.
    new_value = int(request.form.get('new_value'))  # New power value

    # Update the user's power in user_data
    user_data[user_id]['powers'][power_type] = new_value

    # Recalculate bonuses based on updated power values
    bonuses = {
        'Innate': sum(user['powers']['Innate'] for user in user_data.values()),
        'Artifact': sum(user['powers']['Artifact'] for user in user_data.values()),
        'Consumable': sum(user['powers']['Consumable'] for user in user_data.values()),
        'Legendary': sum(user['powers']['Legendary'] for user in user_data.values())
    }

    # Render the updated template with new user_data and bonuses
    return render_template('index.html', user_data=user_data, bonuses=bonuses)


@app.route('/activate', methods=['POST'])
def activate_power():
    user = request.form['user']  # Assuming 'user' is the key for the username
    power = request.form['power']  # The power being activated

    # Get the current power value
    current_power_value = user_data[user]['powers'][power]

    # Check if the power is negative
    if current_power_value < 0:
        user_data[user]['funbucks'] += 10  # Gain 10 Funbucks if the power was negative
    else:
        # Deduct Funbucks based on the current power value (including the first activation)
        deduction_amount = 10 * (current_power_value + 1)  # Increment the power for deduction
        user_data[user]['funbucks'] -= deduction_amount  # Deduct even if it causes negative Funbucks

    # Activate the power for the shared pool and count up the usage
    for p in user_data:  # Iterate over all users for shared effects
        # Increment the activated power for the user
        user_data[p]['powers'][power] += 1

        # Decrease the other powers for all users
        for other_power in user_data[p]['powers']:
            if other_power != power:
                user_data[p]['powers'][other_power] -= 1  # Decrease the other powers

    # Calculate bonuses for each power type
    bonuses = {
        'Innate': calculate_bonus(user_data[user]['powers']['Innate']),
        'Artifact': calculate_bonus(user_data[user]['powers']['Artifact']),
        'Legendary': calculate_bonus(user_data[user]['powers']['Legendary']),
        'Consumable': calculate_bonus(user_data[user]['powers']['Consumable'])
    }

    print(f"{user} activated {power}! New charge for {power}: {user_data[user]['powers'][power]}. Funbucks: {user_data[user]['funbucks']}")  # Debug output

    return render_template('index.html', user_data=user_data, bonuses=bonuses)


@app.route('/place_bet', methods=['POST'])
def place_bet():
    user = request.form['user']
    bet_description = request.form['bet_description']
    bet_amount = int(request.form['bet_amount'])
    # Logic to place a bet goes here
    user_data[user]['funbucks'] -= bet_amount
    user_data[user]['bets'].append({'description': bet_description, 'amount': bet_amount})
    return redirect('/')

@app.route('/resolve_bet', methods=['POST'])
def resolve_bet():
    user = request.form['user']
    bet_index = int(request.form['betIndex'])
    result = request.form['result']
    # Logic to resolve the bet goes here
    bet = user_data[user]['bets'][bet_index]
    if result == 'win':
        user_data[user]['funbucks'] += bet['amount'] * 2  # Example: double the bet amount
    user_data[user]['bets'].pop(bet_index)
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the port provided by Render
    app.run(host='0.0.0.0', port=port)
