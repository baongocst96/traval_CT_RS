# -*- coding: utf-8 -*-
from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk import Tracker, Action
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction
from rasa_sdk.executor import CollectingDispatcher
import json, datetime, yaml, re
from rasa_sdk.events import SlotSet, Restarted, AllSlotsReset
import sqlite3, logging
from rasa_sdk.interfaces import ActionExecutionRejection
from deepai_nlp.utils import remove_tone_line
from rasa_sdk.events import ReminderScheduled, Form


logger = logging.getLogger(__name__)
REQUESTED_SLOT = "requested_slot"

class DulichForm(FormAction):
    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""

        pass
    def chitchat(self, dispatcher, tracker):
        dictmes = tracker.latest_message
        intent = dictmes['intent']['name']
        try:
            dispatcher.utter_template("utter_"+intent, tracker)
        except: 
            print('intennnnn: ',intent)
            pass
    
    def validate_slots(self, slot_dict, dispatcher, tracker, domain):
        # type: (Dict[Text, Any], CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        """Validate slots using helper validation functions.

        Call validate_{slot} function for each slot, value pair to be validated.
        If this function is not implemented, set the slot to the value.
        """

        for slot, value in list(slot_dict.items()):
            validate_func = getattr(
                self, "validate_{}".format(slot), lambda *x: {slot: value}
            )
            # if tracker.latest_message.get('text').lower() == 'exit':
            #     print("EXITTTTTTTTTTTT")
            #     return[Restarted()]
            validation_output = validate_func(value, dispatcher, tracker, domain)
            print("showw wwwwwww", validation_output, type(validation_output))
            #show chitchat when type intent chitchat
            try:
                if list(validation_output.values())[0] is None:
                    print('********** entity is None')
                    self.chitchat(dispatcher, tracker)
            except:
                pass
            if not isinstance(validation_output, dict):
                logger.warning(
                    "Returning values in helper validation methods is deprecated. "
                    + "Your `validate_{}()` method should return ".format(slot)
                    + "a dict of {'slot_name': value} instead."
                )
                validation_output = {slot: validation_output}
            slot_dict.update(validation_output)

        # validation succeed, set slots to extracted values
        return [SlotSet(slot, value) for slot, value in slot_dict.items()]
    def validate(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        """Extract and validate value of requested slot.

        If nothing was extracted reject execution of the form action.
        Subclass this method to add custom validation and rejection logic
        """

        # extract other slots that were not requested
        # but set by corresponding entity or trigger intent mapping
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)

        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher, tracker, domain))            
            if tracker.latest_message.get('text').lower() == 'exit':
                dispatcher.utter_message("da bam vao nut exit roi do");
                print ("in ra cai gì nè", slot_values)
                raise ActionExecutionRejection(
                        self.name(),
                        "Failed to extract slot {0} "
                        "with action {1}"
                        "".format(slot_to_fill, self.name()),
                    )
            if not slot_values:
                print(" alo alo ")
                if tracker.latest_message.get('intent').get('name') == 'exit' \
                        or remove_tone_line(tracker.latest_message.get('text').lower()) == 'yeu cau khac':
                    raise ActionExecutionRejection(
                        self.name(),
                        "Failed to extract slot {0} "
                        "with action {1}"
                        "".format(slot_to_fill, self.name()),
                    )
                else:
                    pass

        logger.debug("Validating extracted slots: {}".format(slot_values))
        return self.validate_slots(slot_values, dispatcher, tracker, domain)