from flask import Flask, render_template, request, jsonify
import aiml
import os
import urllib2
import json
from google import google
from textblob import TextBlob
from googleplaces import GooglePlaces, types, lang

#################### FOR EXTRACTING PLACES ###############################

import nltk
#nltk.download('all')

def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names

#line = "weather in Hyderabad and Mumbai"
   
############################################################################

#################### FOR INFORMING ABOUT WEATHER CONDITIONS ################
import forecastio

api_key = "b1c22e5e1e6283c35828404f63be6b7e"
#lat = -31.967819
#lng = 115.87718

#forecast = forecastio.load_forecast(api_key, lat, lng)

#used dark sky api
#url ='https://api.darksky.net/forecast/81b26981aa02943d6e98be4c463e666c/17.544329,78.571895'
#use of the json file along with our campus cordinates
#json_obj =urllib2.urlopen(url)

#data = json.load(json_obj)

#print data['currently'] #prints the entire dictionary

############################################################################

############ FOR SUGGESTING NEARBY PLACES ####################

YOUR_API_KEY = 'AIzaSyA-f0OCAV_R5_-uLyGFsjs2UDxNfy63gYk '


google_places = GooglePlaces(YOUR_API_KEY)

query_result = google_places.text_search(
    query='mumbai' ,
    radius=1000)
#{'lat':19.148320, 'lng':72.888794}
#query_result = google_places.nearby_search(
#    location='mumbai,India', keyword='Restaurants',
#    radius=1000, types=[types.TYPE_RESTAURANT])

#if query_result.has_attributions:
#   print query_result.html_attributions


for place in query_result.places:
    print place.name
    cod = place.geo_location
    
    print cod['lat']
    print cod['lng']
    
#    print place.place_id  
    # The following method has to make a further API call.
    place.get_details()
    # Referencing any of the attributes below, prior to making a call to
    # get_details() will raise a googleplaces.GooglePlacesAttributeError.
    #print place.details # A dict matching the JSON response from Google.
    #print place.local_phone_number
    #print place.international_phone_number
    #print place.website
    #print place.url
################################
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('chat.html')

@app.route("/ask", methods=['POST'])
def ask():
	message = str(request.form['messageText'])

	kernel = aiml.Kernel()

	if os.path.isfile("bot_brain.brn"):
	    kernel.bootstrap(brainFile = "bot_brain.brn")
	else:
	    kernel.bootstrap(learnFiles = os.path.abspath("aiml/std-startup.xml"), commands = "load aiml b")
	    kernel.saveBrain("bot_brain.brn")

	# kernel now ready for use
	while True:
	    if message == "quit":
	        exit()
	    elif message == "save":
	        kernel.saveBrain("bot_brain.brn")
	        
	    elif message == "hey":
	       
	        return jsonify({'status':'OK','answer':"hey, how can I help?"})
	        
	    else:
                
#                if "about" in message:
#	            search_results = google.search(message)
#                    bot_response = search_results[1].description
#                elif "weather" in message:
                #query_result = google_places.text_search(query= message ,radius=1000)
                #for place in query_result.places:
                #    print place.name
                #    cod = place.geo_location
                
                #    lat = cod['lat']
                #    lng = cod['lng']
                    sentences = nltk.sent_tokenize(message)
                    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
                    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
                    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

                    entities = []
                    for tree in chunked_sentences:
                      entities.extend(extract_entity_names(tree))
                    #print(entities)
                    
                    for entity in entities:
                      query_result = google_places.text_search(query= entity ,radius=1000)
                      for place in query_result.places:
                          print place.name
                          cod = place.geo_location
                
                          lat = cod['lat']
                          lng = cod['lng']
                          forecast = forecastio.load_forecast(api_key, lat, lng)
                          ans = forecast.currently()
                          bot_response = ans.summary      
#                else:   
#                    bot_response = kernel.respond(message)
	                  print(bot_response)
	                  return jsonify({'status':'OK','answer':bot_response})
	        # bot_response = kernel.respond(message)
	        # print bot_response
	       

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
