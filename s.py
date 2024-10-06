from flask import Flask, render_template, redirect, request, flash
import rdflib
from flask_mail import Mail, Message

app = Flask(__name__)

# Setup Flask-Mail
app.secret_key = '1234'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sasa30800@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'sa303930'   # Replace with your password
app.config['MAIL_DEFAULT_SENDER'] = 'sasa30800@gmail.com'
mail = Mail(app)

# RDF graph parsing
g = rdflib.Graph()
g.parse("my_ontology.rdf")

# Function to extract local part of URI
def extract_local_name(uri):
    return uri.split('#')[-1] if '#' in uri else uri
    

@app.route('/subscriber', methods=['POST'])
def Subscriber():
    tourism_places=request.form.get('tourism_places')
    Activity = request.form.get('Activity')
    regions = request.form.get('regions')
    

    # SPARQL query with data properties (name, address, fee)
    q1 = """
    PREFIX ab: <http://www.semanticweb.org/shoogaldosari/ontologies/2024/4/ontologybuilding#>
    SELECT ?tourism_places ?Activity ?regions ?tourist ?fee 
    WHERE {
        ?tourism_places ab:hasActivity ?Activity;
                        ab:located_in ?regions;
                        ab:suitableFor ?tourist;
                        ab:hasEntryFee ?fee.
        FILTER regex(str(?Activity), \"""" + Activity + """\", "i")
        FILTER regex(str(?regions), \"""" + regions + """\", "i")

    }
    """
    
    tourism_places_data = []
    for r in g.query(q1):
        tourism_places_data.append({
            'tourism_places': extract_local_name(r['tourism_places']),
            'Activity': extract_local_name(r['Activity']),
            'regions': extract_local_name(r['regions']),
            'tourist': extract_local_name(r['tourist']),
             'fee': extract_local_name(r['fee']),
        })
    
   
    return render_template('subscriber.html', tourism_places_data=tourism_places_data)
# Route for Events Query
@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        # When form is submitted (POST request)
        eventType = request.form.get('eventType')
        region = request.form.get('regions')

        # Query the ontology with the submitted form data
        q = """
        PREFIX ab: <http://www.semanticweb.org/shoogaldosari/ontologies/2024/4/ontologybuilding#>
        SELECT ?event ?eventType ?regions ?fee ?timeofevent
        WHERE {
            ?event ab:hasEventType ?eventType;
                   ab:event_locatedIn ?regions;
                   ab:event_hasEntryFee ?fee;
                    ab:hastime ?timeofevent.
            FILTER regex(str(?eventType), \"""" + eventType + """\")
        }
        """
        
        event_data = []
        for r in g.query(q):
            event_data.append({
                'event': extract_local_name(r['event']),
                'eventType': extract_local_name(r['eventType']),
                'regions': extract_local_name(r['regions']),
                'fee': extract_local_name(r['fee']),
                'timeofevent': extract_local_name(r['timeofevent']),
            })
        
        # Render the results after form submission
        return render_template('events.html', event_data=event_data)

    # For GET request, show the form to input eventType and regions
    return render_template('event_form.html')

    
# Route to display the 'Be part of tourism' form
@app.route('/be_part_of_tourism')
def be_part_of_tourism():
    return render_template('be_part_of_tourism.html')

# Route to handle form submission and send email
@app.route('/submit_form', methods=['POST'])
def submit_form():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Send email
    try:
        msg = Message('New Tourism Submission',
                      recipients=['sasa30800@gmail.com'])  # Replace with your email
        msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        mail.send(msg)
        flash('Thank you! Your submission has been received.', 'success')
    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'danger')

    return redirect('/be_part_of_tourism')

@app.route('/index')
def hello_world():
    return render_template('index.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/')
def Main_Redirection():
    return redirect('/index')

@app.route('/<string:url>')
def Routes_Redirection(url):
    return redirect('/index')

if __name__ == '__main__':
    app.run(debug=True)
