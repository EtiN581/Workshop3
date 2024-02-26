"""
Practical Exercise: From Local to Decentralized Computation
Participants should form groups of 3 to 5 and select a simple dataset, such as Iris, Housing Market, or Titanic, 
for the following activities:

Q1: Develop diverse predictive models targeting the selected dataset. 
Each group member should create a distinct model.
💡 Basic flask app
Evaluate the accuracy and performance of your model.
Adapt your model for API access. This API should include a GET predict route that accepts model arguments and 
returns a prediction. Determine a standardized API response format within your group.
"""
input()
try:
    from flask import Flask
    import seaborn as sns

    df = sns.load_dataset('titanic')
    print(df)

except Exception as e:
    print(e)
    input()
"""
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
    
    
app.run(host="0.0.0.0")
"""


"""
Q2: Generate a consensus prediction by averaging outputs from the group's models, using tools like ngrok for 
inter-computer connectivity. Assess the performance of this aggregated meta-model.

This stage illustrates the creation of a distributed prediction system in a trusted environment. 
The next step involves opening the model to external contributions, which may come from both benign 
and malicious actors.

Introducing Consensus with Slashing Mechanism
Q3: Introduce a weighting system to refine the meta-model's predictions. Weights, ranging from 0 to 1, are 
adjusted with each prediction batch to reflect the accuracy of individual models relative to the group consensus.

Q4: Implement a proof-of-stake consensus mechanism with a slashing protocol. Models must make an initial deposit 
(e.g., 1000 euros) upon registration to participate. This deposit serves as a security measure, ensuring 
participants' commitment to the network's integrity.

Implement penalties (slashing) for actions that undermine network accuracy or trustworthiness. For example, 
consistently inaccurate predictions may result in a loss of deposit. This protocol discourages adverse behaviors 
while encouraging contributions of accurate, reliable predictions. Adjust model weights based on performance and 
penalties, promoting a merit-based system that rewards accuracy and penalizes dishonesty or inaccuracy. Incorporating 
a slashing mechanism enhances the network's reliability and accountability, ensuring that contributions are both 
accurate and made in good faith, thus maintaining the integrity and effectiveness of the decentralized prediction 
system.

To simplify the implementation asume that balance and slashing are done locally. 
Create a Json Database were you track model balance.
"""
input()