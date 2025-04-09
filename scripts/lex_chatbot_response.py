def lambda_handler(event, context):
    user_input = event['inputTranscript'].lower()

    if "väder" in user_input:
        return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled",
                                 "message": {"contentType": "PlainText", "content": "Vädret hämtas från SMHI..."}}}

    elif "blad" in user_input:
        return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled",
                                 "message": {"contentType": "PlainText", "content": "Analyserar blad via bildanalys..."}}}

    elif "bevattning" in user_input:
        return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled",
                                 "message": {"contentType": "PlainText", "content": "Jag kollar sensorvärden..."}}
                }

    return {"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled",
                             "message": {"contentType": "PlainText", "content": "Kan du omformulera frågan?"}}}
