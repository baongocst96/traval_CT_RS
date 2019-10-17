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
            print("showw wwwwwww", validation_output)
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
            print ("in ra cai gì nè", slot_values)
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

class VnptForm(FormAction):

    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""

        pass

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

            if not slot_values:
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

    def run(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        """Execute the side effects of this form.

        Steps:
        - activate if needed
        - validate user input if needed
        - set validated slots
        - utter_ask_{slot} template with the next required slot
        - submit the form if all required slots are set
        - deactivate the form
        """

        # activate the form
        events = self._activate_if_required(dispatcher, tracker, domain)
        # validate user input
        events.extend(self._validate_if_required(dispatcher, tracker, domain))
        # schedule reminder
        reminder = ReminderScheduled("action_restart", datetime.datetime.now())
        events.append(reminder)
        # check that the form wasn't deactivated in validation
        if Form(None) not in events:

            # create temp tracker with populated slots from `validate` method
            temp_tracker = tracker.copy()
            for e in events:
                if e["event"] == "slot":
                    temp_tracker.slots[e["name"]] = e["value"]

            next_slot_events = self.request_next_slot(dispatcher, temp_tracker, domain)

            if next_slot_events is not None:
                # request next slot
                events.extend(next_slot_events)
            else:
                # there is nothing more to request, so we can submit
                self._log_form_slots(tracker)
                logger.debug("Submitting the form '{}'".format(self.name()))
                events.extend(self.submit(dispatcher, temp_tracker, domain))
                # remove reminder
                events.remove(reminder)
                # deactivate the form after submission
                events.extend(self.deactivate())
        return events

class ViTri(Action):
    def name(self) -> Text:
        return "action_traval_detail"

    def forrmat_payload(self, key, value):
        enti = {key:value.lower()}
        return json.dumps(enti)

    def list_button(seft, thong_tin):
        buttons = []
        buttons.append({
            "title":"🔍🔍 thông tin "+thong_tin,
            "payload":"/request_thongtin{}".format(seft.forrmat_payload("thong_tin", thong_tin))
            })
        buttons.append({
            "title":"🚗 địa chỉ "+thong_tin,
            "payload" : "/request_vitri{}".format(seft.forrmat_payload("vi_tri", thong_tin))
            })
        buttons.append({
            "title":"🏄🏾‍♂️🏄🏾‍♂️ chơi gì ở "+thong_tin,
            "payload":"/request_hoatdong{}".format(seft.forrmat_payload("hoat_dong", thong_tin))
            })
        buttons.append({
            "title":"🏦🏦 chi phí ở "+thong_tin,
            "payload":"/request_chiphi{}".format(seft.forrmat_payload("chi_phi", thong_tin))
            })
        buttons.append({
            "title":"🏞🏞 khám phá địa điểm khác",
            "payload":"/request_chung"
            })

        return buttons

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> List[Dict]:
        
        dict_intent = {
        "request_vitri": "vi_tri",
        "request_thongtin": "thong_tin",
        "request_hoatdong": "hoat_dong",
        "request_chiphi": "chi_phi"
        }
        dict_thongtinct = {
        "bến ninh kiều":{
            "thong_tin": "Theo Wiki: Bến Ninh Kiều là một địa danh du lịch có từ lâu và hấp dẫn du khách bởi phong cảnh sông nước hữu tình và vị trí thuận lợi nhìn ra dòng sông Hậu. Từ lâu bến Ninh Kiều đã trở thành biểu tượng về nét đẹp thơ mộng bên bờ sông Hậu của cả Thành phố Cần Thơ, thu hút nhiều du khách đến tham quan và đi vào thơ ca.",
            "hoat_dong": "Ăn uống, chụp hình, đi dạo",
            "chi_phi": "không có vé vào cổng, đồ ăn giá cả hợp lý ",
            "img":"https://i.ibb.co/TWnF0nn/ben-ninh-kieu.jpg",
            "vi_tri":"Nằm ở: 38 Hai Bà Trưng, ​​Tân An, Ninh Kiều, Cần Thơ \n Bạn có thể di chuyển bằng ô tô hoặc xe máy đén đó"
            },
        "chợ đêm":{
            "thong_tin": "Ở đây có bán rất nhiều món ngon, trong đó có những món đặc trưng của miền Tây mà tiêu biểu là những món chè",
            "hoat_dong": "Ăn uống, chụp hình, đi dạo, shopping",
            "chi_phi": "không có vé vào cổng, đồ ăn ngon, quần áo giá cả hợp lý",
            "img":"https://i.ibb.co/kSntHQB/cho-dem.png",
            "vi_tri":"Nằm ở: Hai Bà Trưng, Tân An, Ninh Kiều, Cần Thơ, Việt Nam \n Bạn có thể di chuyển bằng ô tô hoặc xe máy đén đó" 
            },
        "nhà cổ bình thủy":{
            "thong_tin": "Bằng giá trị kiến trúc, lịch sử của mình, nhà cổ Bình Thủy đã được công nhận là “di tích nghệ thuật cấp quốc gia”, ngày càng thu hút nhiều khách đến thăm cũng như các đoàn làm phim về mượn bối cảnh cho những thước phim của mình.",
            "hoat_dong": "tham quan , chụp ảnh",
            "chi_phi": "không có vé vào cổng",
            "img":"https://i.ibb.co/2szXWhJ/nha-co-binh-thuy.jpg",
            "vi_tri":"Nằm ở: 144 Bùi Hữu Nghĩa, Bình Thuỷ, Bình Thủy, Cần Thơ, Việt Nam \n\ Bạn có thể di chuyển bằng ô tô hoặc xe máy đén đó"
            },
        "vườn cây mỹ khánh":{
            "thong_tin": "Đặt chân tới vườn trái cây này thì bạn sẽ được tham quan hơn 20 giống cây trồng khác nhau sẽ cho bạn một trải nghiệm đặc biệt.",
            "hoat_dong": "tham quan , chụp ảnh, hái trái cây tại vườn và các trò chơi dân gian hấp dẫn",
            "chi_phi": "vé vào cổng 20k/ng, hái trái cây ăn tại vườn, mang về tính theo giá của vườn",
            "img":"https://i.ibb.co/gRV11df/my-khanh.jpg",
            "vi_tri":"Nằm ở: Mỹ Khánh, Phong Điền, Cần Thơ, Việt Nam \n Bạn có thể di chuyển bằng ô tô hoặc xe máy đén đó"
            },
        "chợ nổi cái răng":{
            "thong_tin": "Theo Wiki: Chợ nổi Cái Răng là chợ nổi chuyên trao đổi, mua bán nông sản, các loại trái cây, hàng hóa, thực phẩm, ăn uống ở trên sông và là điểm tham quan đặc sắc của quận Cái Răng, thành phố Cần Thơ",
            "hoat_dong": "tham quan , chụp ảnh, đi thuyền tham quan chợ nổi",
            "chi_phi": "vé tham quan bằng thuyên 200k/ng",
            "img":"https://i.ibb.co/Xsy46sH/cho-noi-cai-rang.jpg",
            "vi_tri":"Nằm ở: 46 Hai Bà Trưng, Lê Bình, Cái Răng, Cần Thơ \n Bạn có thể di chuyển bằng ô tô hoặc xe máy đến bến tàu dau đó thuê thuyền để tham quan trợ nổi"
            }

        }
        if  tracker.latest_message['intent'].get('name') == 'request_chung':
            intro = "Đến tới Cần Thơ thì bạn không thể bỏ qua các địa điểm như Bến Ninh Kiều, Chùa Ông, Chợ Đêm, nhà cổ Bình Thủy, Vườn cây Mỹ Khánh, Thiền Viện Trúc Lâm"
            buttons=[]
            for keys, text in dict_thongtinct.items():
                buttons.append({
                    "title":keys,
                    "payload": "/request_thongtin{}".format(self.forrmat_payload("thong_tin", keys))
                    })
            dictmes = tracker.latest_message
            mes = dictmes['text']
            conn = sqlite3.connect('/media/baongocst/Free/sqlite3/chatbot_dulich.db')
            c = conn.cursor()
            sql = "insert into chatbot(questions) values('%s')"%mes
            print(sql)
            c.execute(sql)
            conn.commit()
            conn.close()
            dispatcher.utter_button_message(intro, buttons=buttons)
        else:
            intent_name = tracker.latest_message['intent'].get('name')
            try:
                slot_name = dict_intent[intent_name]
            except:
                print("error false intent")
                return[]

            thong_tin = next(tracker.get_latest_entity_values(slot_name), None)
            print("Thong tin ", thong_tin)
            # thong_tin = tracker.get_slot(slot_name)
            thong_tin = thong_tin.replace('_',' ')
            ask = dict_thongtinct[thong_tin][slot_name]
            buttons = self.list_button(thong_tin)
            if(intent_name == 'request_thongtin'):  
                dispatcher.utter_media(dict_thongtinct[thong_tin]['img'])
            dispatcher.utter_button_message(ask,buttons=buttons)

        
        return []

        ##if any(tracker.get_latest_entity_values("CT"))

# find hottel 
# sear hottel with location and quality
# show infor hottel, view price, price, adress 
# => form book room

class find_hottel(Action):
    def name(self) -> Text:
        return "action_find_hottel"

    def forrmat_payload(self, enti):
        return json.dumps(enti)

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> List[Dict]:
        
        dict_listhottel = {
        "khach san TTC":
            {
            "name_hottel":"khach san TTC",
            "lc_hottel":"quận ninh kiều",
            "qu_hottel":"khách sạn chất lượng",
            "img_hottel":"https://i.ibb.co/4gLN0PC/ttc-hottel.jpg",
            "adress_Hottel":"312/2 Bến Ninh kiều thành phố cần thơ",
            "detail": "khách sạn sạch sẻ thoáng mát đêm 500k",
            "price":"500"
            },
        "khach san Tây Nam":
            {
            "name_hottel":"khach san Tây Nam",
            "lc_hottel":"quận cái răng",
            "qu_hottel":"khách sạn chất lượng",
            "img_hottel":"https://i.ibb.co/GnSXWT2/taynam-hottel.jpg",
            "adress_Hottel":"312/2 câù quang trung thành phố cần thơ",
            "detail": "khách sạn sạch sẻ thoáng mát đêm 300k",
            "price":"300"
            }
        }

        menu_show = {
        "name_hottel":"Tên khách sạn",
        "lc_hottel":"Khu vực",
        "qu_hottel":"Loại khách sạn",
        "adress_Hottel":"Địa chỉ",
        "detail":"Thông tin chung",
        "price":"Tầm Giá"
        }

        if  tracker.latest_message['intent'].get('name') == 'request_hottel':
            if any(tracker.get_latest_entity_values("lc_hottel")):
                lc_hottel = next(tracker.get_latest_entity_values("lc_hottel"), None)  ## value entity 
            else:
                intro = "Dưới đây là một vài gợi ý phù hợp cho bạn:"				
                buttons = []
                for keys, text in dict_listhottel.items():					
                    buttons.append({
                        "title":keys,
                        "payload": "/info_hottel{}".format(self.forrmat_payload({"name_hottel": dict_listhottel[keys]['name_hottel']}))
                        })
                dispatcher.utter_button_message(intro,buttons=buttons)  
        if tracker.latest_message['intent'].get('name') == 'info_hottel':
            info = dict_listhottel[next(tracker.get_latest_entity_values("name_hottel"), None)]
            detail = ''
            for key, text in info.items():
                if(key != 'img_hottel'):
                    detail += str(menu_show[key]) + ' : ' + text + '\n\n\n' 
            dispatcher.utter_media(info['img_hottel'])
            bt_datphong = []
            bt_datphong.append({
                "title":"Đặt phòng",
                "payload":"/form_hottel{}".format(self.forrmat_payload({'lc_hottel':info['lc_hottel'], 'qu_hottel':info['qu_hottel']}))
                })
            bt_datphong.append({
                "title":"chọn khách sạn khác",
                "payload":"/request_hottel"
                })

            dispatcher.utter_button_message(detail,buttons=bt_datphong)

# form book hottel 
# request numberroom, time, sdt
# show kq
class HottelForm(DulichForm):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "hottel_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["name_hottel","num_room", "time", "sdt", "note_hottel"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "time": [
            self.from_entity(entity="time"),
            self.from_text()
            ],
            "num_room":  [
            self.from_entity(entity="num_room"),
            self.from_text()
            ],					  
            "sdt": self.from_text(),
            "name_hottel":[
            self.from_entity(entity="name_hottel"),
            self.from_text()
            ],
            "note_hottel": self.from_text()		   
            
        }

    def forrmat_payload(self, enti):
        return json.dumps(enti)

    # USED FOR DOCS: do not rename without updating in docs
    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer"""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_sdt(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        
        import re

        pattern = "^(0)[0-9]{9}"
        z = re.match(pattern, value)
    
        if z and len(value) == 10:
            return {"sdt": value}
        else:
            dispatcher.utter_template("utter_wrong_phone", tracker)
            return {"sdt": None}

    def validate_num_room(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        if any(tracker.get_latest_entity_values("num_room")):
            return {"num_room": value}
        if self.is_int(value) and int(value) > 0:
            return {"num_room": value}
        else:
            self.chitchat(dispatcher, tracker)
            dispatcher.utter_template("utter_wrong_num_room", tracker)
            return {"num_room": None}
    
    def show_date(self,n):
        day = datetime.datetime.today() + datetime.timedelta(days=1)
        return day.strftime ('%d-%m-%Y')

    def validate_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        if any(tracker.get_latest_entity_values("time")) or any(tracker.get_slot("time")):
            switcher = {
                'ngày_mai':self.show_date(1),
                'ngày_kia':self.show_date(2),
                'hôm_nay':self.show_date(0)
            }
            value = switcher.get(value, value)
            return {"time": value}
        else:
            wrong_time = "!!!🥴 Hãy nhập thời gian cụ thể: \n\n\n Ex: ngày mai, ngày kia, ngày 09/01,..."
            
            dispatcher.utter_message(wrong_time)
            return {"time": None}

       
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        info={
        "name_hottel":tracker.get_slot('name_hottel'),
        "num_room":tracker.get_slot('num_room'),
        "sdt":tracker.get_slot('sdt'),
        "time":tracker.get_slot('time'),
        "note_hottel":tracker.get_slot('note_hottel')
        }
        text_info = ''
        for key, text in info.items():
            text_info += str(key) + ' : ' + str(text) + '\n\n\n'
        buttons= [{
            "title":"Đồng ý",
            "payload":"/agreehottel"
            },
            {
            "title":"Chọn khách sạn khác",
            "payload":"/request_hottel"
            },
            {
            "title":"Thay đổi thong tin",
            "payload":"/request_editHottel"
            }]
        dispatcher.utter_button_message(text_info, buttons=buttons)
        return []

## change info hottel
# chose info to change 
# chang info to utter done 

class Restart_hottel(Action):
    def name(self) -> Text:
        return "restart_form_hottel"
    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> List[Dict]:
        return[
            SlotSet("sdt", None),
            SlotSet("num_room", None),
            SlotSet("time", None),
            SlotSet("note_hottel", None)
        ]
        
## restaurant

class FindRestaurantToBook(Action):
    def name(self) -> Text:
        return "action_find_res_to_book"

    @staticmethod
    def db_name() -> Dict[Text, Any]:
        return {
            "ChIJeS6zcfuvCjERtN0GaPDQoBw": "Nhà hàng Ngọc Gia Trang",
            "ChIJMyTxJeqvCjERoiAEm1aMnLA": "Nhà hàng Sông Tiền",
            "ChIJx6-nJPavCjERfip2XNPNxoQ": "Nhà hàng hải sản Phố Biển",
            "ChIJdT4xNPCvCjERii0h_4iJHzQ": "Quán ăn Lộc Phố",
            "ChIJL0S5MamlCjERoxY9U1uAF9c": "Nhà hàng Mekong Taste",
            "ChIJF-i2aXalCjERI2uZb6b-8kQ": "Nhà hàng Thới Sơn",
            "ChIJYXKWUaq6CjERMMh5EG--xJk": "Nhà hàng Trung Lương",
            "ChIJh36_ePuvCjERsrcMdlZzHGw": "Nhà hàng Làng Việt",
            "ChIJ4-jigfKvCjERyEH2_BC_7u8": "Nhà hàng Chương Dương",
            "ChIJp_0PMsOvCjERxoWVnQ1-Ils": "Quán ăn Tạ Hiền",
            "ChIJb5rGx_CvCjERceuwJqes_Ls": "Nhà hàng Mỹ Phúc",
            "ChIJu6cpKPqvCjER3FGV3WyOXhA": "Quán ăn Đồng Nam",
            "ChIJ9QteN-qvCjERkf2Owo0MXG4": "Nhà hàng Quê Hương"
        }
    def forrmat_payload(self, enti):
        return json.dumps(enti)

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
        ) -> List[Dict]:

        # retrieve google api key		
        with open("./ga_credentials.yml", 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        key = cfg['credentials']['GOOGLE_KEY']

        '''
        # get user's current location		
        get_origin = requests.post(
            "https://www.googleapis.com/geolocation/v1/geolocate?key={}".format(key)).json()
        
        origin_lat = get_origin['location']['lat']
        origin_lng = get_origin['location']['lng']
        '''
        # info = []

        # for i in self.db_name().keys():
        #	 place = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?origins=place_id:{}&destinations=place_id:{}&language={}&key={}'
        #					 .format("ChIJUx33J-uvCjERcVVUDPqhLak", i, "vi", key)).json()
        #	 info.append({
        #		 "name": self.db_name()[i],
        #		 "distance_text": place['rows'][0]['elements'][0]['distance']['text'],
        #		 "distance_value": place['rows'][0]['elements'][0]['distance']['value'],
        #		 "duration": place['rows'][0]['elements'][0]['duration']['text']
        #		 })

        info = [
            {
                'name': 'Nhà hàng Sông Tiền', 
                'distance_text': '4,5 km', 
                'distance_value': 4511, 
                'duration': '10 phút',
                'image_res':'https://i.ibb.co/M84HxVj/res.jpg',
                'menu_res':'https://i.ibb.co/k30xHBs/menu.jpg'
            }, 
            {
                'name': 'Nhà hàng Quê Hương', 
                'distance_text': '4,6 km', 
                'distance_value': 4587, 
                'duration': '10 phút',
                'image_res':'https://i.ibb.co/GcgT4ct/res1.jpg',
                'menu_res':'https://i.ibb.co/gZc4H5q/menu2.jpg'
            }, 
            {
                'name': 'Nhà hàng Chương Dương', 
                'distance_text': '4,7 km', 
                'distance_value': 4690, 
                'duration': '11 phút',
                'image_res':'https://i.ibb.co/7zwrg3j/res2.jpg',
                'menu_res':'https://i.ibb.co/xMDr6Wg/menu3.jpg'
            }, 
            {
                'name': 'Quán ăn Tạ Hiền', 
                'distance_text': '4,7 km', 
                'distance_value': 4715, 
                'duration': '9 phút',
                'image_res':'https://i.ibb.co/4wbDhwt/res3.jpg',
                'menu_res':'https://i.ibb.co/VLY6v1x/menu2.jpg'
            }, 
            {
                'name': 'Quán ăn Lộc Phố', 
                'distance_text': '5,8 km', 
                'distance_value': 5813, 
                'duration': '14 phút',
                'image_res':'https://i.ibb.co/M84HxVj/res.jpg',
                'menu_res':'https://i.ibb.co/k30xHBs/menu.jpg'
            }, 
            {
                'name': 'Nhà hàng Mỹ Phúc', 
                'distance_text': '6,1 km', 
                'distance_value': 6121, 
                'duration': '14 phút',
                'image_res':'https://i.ibb.co/GcgT4ct/res1.jpg',
                'menu_res':'https://i.ibb.co/VLY6v1x/menu2.jpg'
            }, 
            {
                'name': 'Quán ăn Đồng Nam', 
                'distance_text': '6,7 km', 
                'distance_value': 6694, 
                'duration': '15 phút',
                'image_res':'https://i.ibb.co/7zwrg3j/res2.jpg',
                'menu_res':'https://i.ibb.co/gZc4H5q/menu2.jpg'
            }, 
            {
                'name': 'Nhà hàng hải sản Phố Biển', 
                'distance_text': '7,0 km', 
                'distance_value': 6972, 
                'duration': '16 phút',
                'image_res':'https://i.ibb.co/4wbDhwt/res3.jpg',
                'menu_res':'https://i.ibb.co/xMDr6Wg/menu3.jpg'
            }, 
            {
                'name': 'Nhà hàng Làng Việt', 
                'distance_text': '7,5 km', 
                'distance_value': 7461, 
                'duration': '15 phút',
                'image_res':'https://i.ibb.co/M84HxVj/res.jpg',
                'menu_res':'https://i.ibb.co/k30xHBs/menu.jpg'
            }, 
            {
                'name': 'Nhà hàng Ngọc Gia Trang', 
                'distance_text': '7,5 km', 
                'distance_value': 7503, 
                'duration': '15 phút',
                'image_res':'https://i.ibb.co/GcgT4ct/res1.jpg',
                'menu_res':'https://i.ibb.co/VLY6v1x/menu2.jpg'
            }, 
            {
                'name': 'Nhà hàng Trung Lương', 
                'distance_text': '9,9 km', 
                'distance_value': 9922, 
                'duration': '17 phút',
                'image_res':'https://i.ibb.co/7zwrg3j/res2.jpg',
                'menu_res':'https://i.ibb.co/gZc4H5q/menu2.jpg'
            }, 
            {
                'name': 'Nhà hàng Thới Sơn', 
                'distance_text': '12,2 km', 
                'distance_value': 12156, 
                'duration': '25 phút',
                'image_res':'https://i.ibb.co/4wbDhwt/res3.jpg',
                'menu_res':'https://i.ibb.co/xMDr6Wg/menu3.jpg'
            }, 
            {
                'name': 'Nhà hàng Mekong Taste', 
                'distance_text': '12,4 km', 
                'distance_value': 12363, 
                'duration': '27 phút',
                'image_res':'https://i.ibb.co/M84HxVj/res.jpg',
                'menu_res':'https://i.ibb.co/k30xHBs/menu.jpg'
            }]

        info.sort(key=lambda x: x['distance_value'])

        msg  = "Dưới đây là thông tin nhà hàng gần nhất Bot có thể giúp bạn đặt bàn nè..."
        dispatcher.utter_message(msg)

        buttons = []
        msg_title = "🔖 Tên: {}\n\
                    \n🗾 Khoảng cách: {}\n\
                    \n⌛ Thời gian đến nơi ước tính: {}".format(info[0]['name'], info[0]['distance_text'], info[0]['duration'])
        enti = {"name_res":"{}".format(info[0]['name'].lower())}
        print(enti)
        enti_json = json.dumps(enti)
        buttons.append({
            "title": "👀 xem chi tiết",
            "payload": "/detail_res{}".format(enti_json)
            })
        # buttons.append({
        #	 "title": "🚸 Chỉ đường",
        #	 "payload": "/direct_place_res{}".format(enti_json)
        #	 })
        buttons.append({
            "title": "➕ More",
            "payload": "/more_res"
            })
        dispatcher.utter_button_message(msg_title, buttons=buttons)
        return [SlotSet("lst_res", info)]

class MoreRestaurantBook(Action):
    def name(self):
        return "action_more_book"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
        ) -> List[Dict]:

        result = tracker.get_slot("lst_res")

        msg = "Thêm 3 nhà hàng nữa cho bạn chọn nè...😍"
        dispatcher.utter_message(msg)

        msg_title = "Tôi có thể làm gì?"
        buttons = []
        for i in [1, 2, 3]:
            msg_in = "🔖 Tên: {}\n\
                    \n🗾 Khoảng cách: {}\n\
                    \n⌛ Thời gian đến nơi ước tính: {}".format(result[i]['name'], result[i]['distance_text'], result[i]['duration'])
            dispatcher.utter_message(msg_in)

            enti = {"name_res":result[i]['name'].lower()}
            enti_json = json.dumps(enti)
            buttons.append({
                "title":"{}".format(result[i]['name']),
                "payload":"/detail_res{}".format(enti_json)
                })

        buttons.append({
            "title":"🤔 Bạn có thể làm gì?",
            "payload":"/what_can_help"
            })

        dispatcher.utter_button_message(msg_title, buttons=buttons)
        return []
class detailRestaurant(Action):
    def name(self):
        return "action_detail_res"
        
    def forrmat_payload(self, enti):
        return json.dumps(enti)
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
        ) -> List[Dict]:
        nameres = tracker.get_slot('name_res')
        result = tracker.get_slot("lst_res")
        info = []
        for i in result:
            if(i['name'].lower() == nameres):
                info = i
                break
        msg_in = "🔖 Tên: {}\n\
                    \n🗾 Khoảng cách: {}\n\
                    \n⌛ Thời gian đến nơi ước tính: {}".format(info['name'], info['distance_text'], info['duration'])
        dispatcher.utter_media(info['image_res'])
        dispatcher.utter_media(info['menu_res'])
        buttons = []
        buttons.append({
            "title": "🏷 Đặt bàn",
            "payload": "/book_restaurant{}".format(self.forrmat_payload({"name_res":info['name']}))
            })
        buttons.append({
            "title":"Back",
            "payload":"/more_res"
        })
        dispatcher.utter_button_message(msg_in, buttons=buttons)
        
    # Book form
class RestaurantForm(FormAction):

    def name(self) -> Text:
        return "restaurant_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        # if any(tracker.get_slot("time")):
        #     SlotSet("time", tracker.get_slot("time"))
        return ["num_people_res", "add_request_res", "phone_res", "time"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "num_people_res": [
                self.from_entity(entity="num_people_res"),
                self.from_text(),
            ],
            "add_request_res": [
                self.from_text()
            ],
            "phone_res": self.from_text(),
            "time":[
                self.from_text(),
                self.from_entity(entity="time")
            ]
        }

    @staticmethod
    def is_int(string: Text) -> bool:

        try:
            int(string)
            return True
        except ValueError:
            return False
    def show_date(self,n):
        day = datetime.datetime.today() + datetime.timedelta(days=1)
        return day.strftime ('%d-%m-%Y')

    def validate_num_people_res(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        )-> Optional[Text]:

        if self.is_int(value) and int(value) > 0:
            return {"num_people_res": value}
        else:
            dispatcher.utter_template("utter_wrong_num_people_res", tracker)
            return {"num_people_res": None}
    
    def validate_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        if any(tracker.get_latest_entity_values("time")):
            switcher = {
                'ngày_mai':self.show_date(1),
                'ngày_kia':self.show_date(2),
                'hôm_nay':self.show_date(0)
            }
            value = switcher.get(value, value)
            return {"time": value}
        else:
            wrong_time = "!!!🥴 Hãy nhập thời gian cụ thể: \n\n\n Ex: ngày mai, ngày kia, ngày 09/01,..."
            buttons = [
                {
                    "title":"Ngày mai",
                    "payload":"ngày mai"
                },
                {
                    "title":"Ngày kia",
                    "payload":"ngày kia"
                },
                {
                    "title":"Hôm nay",
                    "payload":"hôm nay"
                }

            ]
            dispatcher.utter_button_message(wrong_time, buttons=buttons)
            return {"time": None}

    def validate_phone_res(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        
        import re

        pattern = "^(0)[0-9]{9}"
        z = re.match(pattern, value)
    
        if z and len(value) == 10:
            return {"phone_res": value}
        else:
            dispatcher.utter_template("utter_wrong_phone", tracker)
            return {"phone_res": None}
            

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        msg = "Đang thiết lập..."		
        dispatcher.utter_message(msg)
        dispatcher.utter_template("utter_confirm_res", tracker)
        return []

class ConfirmTransactionRestaurant(Action):
    def name(self) -> Text:
        return "action_confirm_restaurant"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> List[Dict]:
        msg1 = "Đang thực hiện giao dịch..."
        dispatcher.utter_message(msg1)
        msg2 = "✔ Đã đặt chỗ thành công!\
                \nTrong vòng 5p sẽ có nhân viên liên hệ với bạn."
        dispatcher.utter_message(msg2)
        return []

    ##edit form hottel 

class FormEditRestaurant(FormAction):
    def name(self):
        return "form_edit_res"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        if tracker.get_slot("edit_inform_res") == "số người":
            return ["edit_num_people_res"]
        elif tracker.get_slot("edit_inform_res") == "sdt":
            return ["edit_phone_res"]
        elif tracker.get_slot("edit_inform_res") == "time":
            return ["edit_time"]
        else:
            return ["edit_add_request_res"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "edit_num_people_res": [
                self.from_entity(entity="num_people_res"),
                self.from_text(),
            ],
            "edit_phone_res": self.from_text(),
            "edit_add_request_res": [
                self.from_text(),
            ],
            "edit_time:":[
                self.from_text(),
                self.from_entity(entity="time")
            ]
        }

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer"""
    
        try:
            int(string)
            return True
        except ValueError:
            return False
    
    def show_date(self,n):
        day = datetime.datetime.today() + datetime.timedelta(days=1)
        return day.strftime ('%d-%m-%Y')

    def validate_edit_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        if any(tracker.get_latest_entity_values("time")):
            switcher = {
                'ngày_mai':self.show_date(1),
                'ngày_kia':self.show_date(2),
                'hôm_nay':self.show_date(0)
            }
            value = switcher.get(value, value)
            return {"edit_time": value}
        else:
            wrong_time = "!!!🥴 Hãy nhập thời gian cụ thể: \n\n\n Ex: ngày mai, ngày kia, ngày 09/01,..."
            dispatcher.utter_message(wrong_time)
            return {"edit_time": None}

    def validate_edit_num_people_res(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        )-> Optional[Text]:

        if self.is_int(value) and int(value) > 0:
            return {"edit_num_people_res": value}
        else:
            dispatcher.utter_template("utter_wrong_num_people_res", tracker)
            return {"edit_num_people_res": None}

    def validate_edit_phone_res(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:

        pattern = "^(0)[0-9]{9}"
        z = re.match(pattern, value)
    
        if z and len(value) == 10:
            return {"edit_phone_res": value}
        else:
            dispatcher.utter_template("utter_wrong_phone", tracker)
            return {"edit_phone_res": None}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        msg = "Thay đổi của bạn đã đc lưu lại..."
        dispatcher.utter_message(msg)

        if tracker.get_slot("edit_inform_res") == "số người":
            value = tracker.get_slot("edit_num_people_res")
            return [SlotSet("num_people_res", value)]
        elif tracker.get_slot("edit_inform_res") == "sdt":
            value = tracker.get_slot("edit_phone_res")
            return [SlotSet("phone_res", value)]
        elif tracker.get_slot("edit_time") == "time":
            value = tracker.get_slot("edit_time")
            return [SlotSet("time", value)]
        else:
            value = tracker.get_slot("edit_add_request_res")
            return [SlotSet("add_request_res", value)]

class RestarFormEditRes(Action):
    def name(self) -> Text:
        return "restart_form_edit_res"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> List[Dict]:

        return [SlotSet("edit_inform_res", None),
                SlotSet("edit_num_people_res", None),
                SlotSet("edit_inform_res", None),
                SlotSet("edit_add_request_res", None)]

class ActionRestart(Action):
	def name(self)-> Text:
		return "action_restart"

	def run(self,
	   dispatcher: CollectingDispatcher,
	   tracker: Tracker,
	   domain: Dict[Text, Any]
	) -> List[Dict[Text, Any]]:
		return[Restarted()]

class ActionTestDB(Action):
    def name(self)-> Text:
        return "action_test"

    def run(self,
       dispatcher: CollectingDispatcher,
       tracker: Tracker,
       domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:      
    
        mydb = mysql.connector.connect(
           host="localhost",
           user="root",
           passwd="",
           database="chatbot",
           auth_plugin='mysql_native_password'
         )
        sqlht = 'select question from chatbot'
        mycursor = mydb.cursor()
        mycursor.execute(sqlht)
        myresult = mycursor.fetchall()  
        for x in myresult:
            dispatcher.utter_message(x)
        return[]

class ActioncolectDB(Action):
    def name(self)-> Text:
        return "action_collectdb"

    def run(self,
       dispatcher: CollectingDispatcher,
       tracker: Tracker,
       domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        dictmes = tracker.latest_message
        mes = dictmes['text']
        intent = dictmes['intent']['name']
        conn = sqlite3.connect('/media/baongocst/Free/sqlite3/test_nlu.db')
        c = conn.cursor()
        sql = "insert into chatbot(questions, intent) values('%s','%s')"%(mes, intent)
        c.execute(sql)
        conn.commit()
        c.close()
        conn.close()
        return[]


