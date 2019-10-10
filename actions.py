# -*- coding: utf-8 -*-
from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk import Tracker, Action
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction
from rasa_sdk.executor import CollectingDispatcher
import json, datetime

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
            "img":"file:///media/baongocst/Free/projectPY/Nam/images/locations_travel/ben_ninh_kieu.jpg",
            "vi_tri":"Nằm ở: 38 Hai Bà Trưng, ​​Tân An, Ninh Kiều, Cần Thơ \n Bạn có thể di chuyển bằng ô tô hoặc xe máy đén đó"
            },
        "chợ đêm":{
            "thong_tin": "Ở đây có bán rất nhiều món ngon, trong đó có những món đặc trưng của miền Tây mà tiêu biểu là những món chè",
            "hoat_dong": "Ăn uống, chụp hình, đi dạo, shopping",
            "chi_phi": "không có vé vào cổng, đồ ăn ngon, quần áo giá cả hợp lý",
            "img":"file:///media/baongocst/Free/projectPY/Nam/images/locations_travel/cho_dem.png",
            "vi_tri":"Nằm ở: Hai Bà Trưng, Tân An, Ninh Kiều, Cần Thơ, Việt Nam \n Bạn có thể di chuyển bằng ô tô hoặc xe máy đén đó" 
            },
        "nhà cổ bình thủy":{
            "thong_tin": "Bằng giá trị kiến trúc, lịch sử của mình, nhà cổ Bình Thủy đã được công nhận là “di tích nghệ thuật cấp quốc gia”, ngày càng thu hút nhiều khách đến thăm cũng như các đoàn làm phim về mượn bối cảnh cho những thước phim của mình.",
            "hoat_dong": "tham quan , chụp ảnh",
            "chi_phi": "không có vé vào cổng",
            "img":"file:///media/baongocst/Free/projectPY/Nam/images/locations_travel/nha_co_binh_thuy.jpg",
            "vi_tri":"Nằm ở: 144 Bùi Hữu Nghĩa, Bình Thuỷ, Bình Thủy, Cần Thơ, Việt Nam \n\ Bạn có thể di chuyển bằng ô tô hoặc xe máy đén đó"
            },
        "vườn cây mỹ khánh":{
            "thong_tin": "Đặt chân tới vườn trái cây này thì bạn sẽ được tham quan hơn 20 giống cây trồng khác nhau sẽ cho bạn một trải nghiệm đặc biệt.",
            "hoat_dong": "tham quan , chụp ảnh, hái trái cây tại vườn và các trò chơi dân gian hấp dẫn",
            "chi_phi": "vé vào cổng 20k/ng, hái trái cây ăn tại vườn, mang về tính theo giá của vườn",
            "img":"file:///media/baongocst/Free/projectPY/Nam/images/locations_travel/my_khanh.jpeg",
            "vi_tri":"Nằm ở: Mỹ Khánh, Phong Điền, Cần Thơ, Việt Nam \n Bạn có thể di chuyển bằng ô tô hoặc xe máy đén đó"
            },
        "chợ nổi cái răng":{
            "thong_tin": "Theo Wiki: Chợ nổi Cái Răng là chợ nổi chuyên trao đổi, mua bán nông sản, các loại trái cây, hàng hóa, thực phẩm, ăn uống ở trên sông và là điểm tham quan đặc sắc của quận Cái Răng, thành phố Cần Thơ",
            "hoat_dong": "tham quan , chụp ảnh, đi thuyền tham quan chợ nổi",
            "chi_phi": "vé tham quan bằng thuyên 200k/ng",
            "img":"file:///media/baongocst/Free/projectPY/Nam/images/locations_travel/cho_noi_cai_rang.jpg",
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
            dispatcher.utter_button_message(intro, buttons=buttons)
        else:
            intent_name = tracker.latest_message['intent'].get('name')
            slot_name = dict_intent[intent_name]
            thong_tin = next(tracker.get_latest_entity_values(slot_name), None)
            # thong_tin = tracker.get_slot(slot_name)
            thong_tin = thong_tin.replace('_',' ')
            ask = dict_thongtinct[thong_tin][slot_name]
            buttons = self.list_button(thong_tin)
            if(intent_name == 'request_thongtin'):  
                dispatcher.utter_media(dict_thongtinct[thong_tin]['img'], "image")
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
            "img_hottel":"file:///media/baongocst/Free/projectPY/Nam/images/hottel/ttc_hottel.jpg",
            "adress_Hottel":"312/2 Bến Ninh kiều thành phố cần thơ",
            "detail": "khách sạn sạch sẻ thoáng mát đêm 500k",
            "price":"500"
            },
        "khach san Tây Nam":
            {
            "name_hottel":"khach san Tây Nam",
            "lc_hottel":"quận cái răng",
            "qu_hottel":"khách sạn chất lượng",
            "img_hottel":"file:///media/baongocst/Free/projectPY/Nam/images/hottel/taynam_hottel.jpg",
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
            dispatcher.utter_media(info['img_hottel'], "image")
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
class HottelForm(FormAction):
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
        else:
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
        print(info)
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
        