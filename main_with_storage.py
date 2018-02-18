from flask import Flask, render_template, request, jsonify
import aiml
import os
import urllib2
import json
import datetime
import time
import sys
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


#################### FOR INFORMING ABOUT WEATHER CONDITIONS ################
import forecastio
api_key = "81b26981aa02943d6e98be4c463e666c"


############ FOR SUGGESTING NEARBY PLACES  ####################

YOUR_API_KEY = 'AIzaSyAqVsRUECIFIw5qxQfzz7v6kHftZECO6s0'


google_places = GooglePlaces(YOUR_API_KEY)

#query_result = google_places.text_search(
#    query='mumbai' ,
#    radius=1000)
#{'lat':19.148320, 'lng':72.888794}
#query_result = google_places.nearby_search(
#    location='mumbai,India', keyword='Restaurants',
#    radius=1000, types=[types.TYPE_RESTAURANT])

#if query_result.has_attributions:
#   print query_result.html_attributions


#for place in query_result.places:
#    print place.name
#    cod = place.geo_location
    
#    print cod['lat']
#    print cod['lng']
    
#    print place.place_id  
    # The following method has to make a further API call.
#    place.get_details()
    # Referencing any of the attributes below, prior to making a call to
    # get_details() will raise a googleplaces.GooglePlacesAttributeError.
    #print place.details # A dict matching the JSON response from Google.
    #print place.local_phone_number
    #print place.international_phone_number
    #print place.website
    #print place.url
    
#++++++++++++++++++++++++++++
   #query_result = google_places.text_search(query= message ,radius=1000)
                #for place in query_result.places:
                #    print place.name
                #    cod = place.geo_location
                
                #    lat = cod['lat']
                #    lng = cod['lng']
          
################################
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('chat.html')

f = open("output.txt","a")
response = []
query = []

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
            query.append(message)
	    if message == "save":
                endline = "\n"
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                f.write(endline + "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" + endline)
                f.write(endline)
                f.write(st + " | " + endline)
                for x in range(0,len(query)-1):
                    q = query[x]
                    a = response[x]
                    f.write("query: " + q + endline)
                    f.write(a + endline)
                    f.write(endline + "============================================================" + endline)
	        kernel.saveBrain("bot_brain.brn")
                break
	    elif message == "hey":
                response.append("LUCY: hey, how can I help?")
                return jsonify({'status':'OK','answer':"LUCY: hey, how can I help?"})
	        
	    elif "about" in message:
	        search_results = google.search(message)
                response.append(bot_response)
                bot_response = "LUCY: " + search_results[1].description
          
            elif "weather" in message:
                sentences = nltk.sent_tokenize(message)
                tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
                tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
                chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

                entities = []
                for tree in chunked_sentences:
                    entities.extend(extract_entity_names(tree))
                
                if (len(entities) == 0):
                    ans = "LUCY: oh, I'm afraid you'll have to be little specific. e.g Try asking: 'weather in Delhi'"
                    print(ans)
                    response.append(ans)
                    return jsonify({'status':'OK', 'answer': ans})
                    
                list_ans = []
                for entity in entities:
                    query_result = google_places.text_search(query= entity ,radius=1000)
                    for place in query_result.places:
                        print place.name
                        cod = place.geo_location
                
                        lat = cod['lat']
                        lng = cod['lng']
                        forecast = forecastio.load_forecast(api_key, lat, lng)
                        ans = forecast.currently()
                        item = "weather in " + place.name + " is " + ans.summary + " with a temperature of " + str(ans.temperature) + "F"
                        list_ans.append(item)
                final_ans = ""
                for ele in list_ans:
                    final_ans += ele
                    final_ans += '\n'
                bot_response = "LUCY : " + final_ans
                response.append(bot_response)
	        #print(bot_response)
	        return jsonify({'status':'OK','answer':bot_response})
            else:
                bot_response = "LUCY: " + kernel.respond(message)
                response.append(bot_response)
	        #print bot_response
                return jsonify({'status':'OK','answer':bot_response})
        sys.exit(0)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
