from flask import (  # type: ignore not installed in the environment
    Flask,
    Response,
    redirect,
)

app = Flask(__name__)

# Sample XML data
xml_data_1 = """<?xml version="1.0" encoding="UTF-8"?>
<eventList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0" xsi:noNamespaceSchemaLocation="eventList.xsd">
   <output>
      <base_event base_event_id="291" sell_mode="online" title="Camela en concierto">
         <event event_start_date="2021-06-30T21:00:00" event_end_date="2021-06-30T22:00:00" event_id="291" sell_from="2020-07-01T00:00:00" sell_to="2021-06-30T20:00:00" sold_out="false">
            <zone zone_id="40" capacity="243" price="20.00" name="Platea" numbered="true" />
            <zone zone_id="38" capacity="100" price="15.00" name="Grada 2" numbered="false" />
            <zone zone_id="30" capacity="90" price="30.00" name="A28" numbered="true" />
         </event>
      </base_event>
      <base_event base_event_id="322" sell_mode="online" organizer_company_id="2" title="Pantomima Full">
         <event event_start_date="2021-02-10T20:00:00" event_end_date="2021-02-10T21:30:00" event_id="1642" sell_from="2021-01-01T00:00:00" sell_to="2021-02-09T19:50:00" sold_out="false">
            <zone zone_id="311" capacity="2" price="55.00" name="A42" numbered="true" />
         </event>
      </base_event>
      <base_event base_event_id="1591" sell_mode="online" organizer_company_id="1" title="Los Morancos">
         <event event_start_date="2021-07-31T20:00:00" event_end_date="2021-07-31T21:00:00" event_id="1642" sell_from="2021-06-26T00:00:00" sell_to="2021-07-31T19:50:00" sold_out="false">
            <zone zone_id="186" capacity="2" price="75.00" name="Amfiteatre" numbered="true" />
            <zone zone_id="186" capacity="16" price="65.00" name="Amfiteatre" numbered="false" />
         </event>
      </base_event>
   </output>
</eventList>
"""

xml_data_2 = """<?xml version="1.0" encoding="UTF-8"?>
<eventList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0" xsi:noNamespaceSchemaLocation="eventList.xsd">
   <output>
      <base_event base_event_id="291" sell_mode="online" title="Camela en concierto">
         <event event_start_date="2021-06-30T21:00:00" event_end_date="2021-06-30T22:00:00" event_id="291" sell_from="2020-07-01T00:00:00" sell_to="2021-06-30T20:00:00" sold_out="false">
            <zone zone_id="40" capacity="240" price="20.00" name="Platea" numbered="true" />
            <zone zone_id="38" capacity="50" price="15.00" name="Grada 2" numbered="false" />
            <zone zone_id="30" capacity="90" price="30.00" name="A28" numbered="true" />
         </event>
      </base_event>
      <base_event base_event_id="1591" sell_mode="online" organizer_company_id="1" title="Los Morancos">
         <event event_start_date="2021-07-31T20:00:00" event_end_date="2021-07-31T21:20:00" event_id="1642" sell_from="2021-06-26T00:00:00" sell_to="2021-07-31T19:50:00" sold_out="false">
            <zone zone_id="186" capacity="0" price="75.00" name="Amfiteatre" numbered="true" />
            <zone zone_id="186" capacity="14" price="65.00" name="Amfiteatre" numbered="false" />
         </event>
      </base_event>
      <base_event base_event_id="444" sell_mode="offline" organizer_company_id="1" title="Tributo a Juanito Valderrama">
         <event event_start_date="2021-09-31T20:00:00" event_end_date="2021-09-31T21:00:00" event_id="1642" sell_from="2021-02-10T00:00:00" sell_to="2021-09-31T19:50:00" sold_out="false">
            <zone zone_id="7" capacity="22" price="65.00" name="Amfiteatre" numbered="false" />
         </event>
      </base_event>
   </output>
</eventList>
"""

xml_data_3 = """<?xml version="1.0" encoding="UTF-8"?>
<eventList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0" xsi:noNamespaceSchemaLocation="eventList.xsd">
   <output>
      <base_event base_event_id="291" sell_mode="online" title="Camela en concierto">
         <event event_start_date="2021-06-30T21:00:00" event_end_date="2021-06-30T21:30:00" event_id="291" sell_from="2020-07-01T00:00:00" sell_to="2021-06-30T20:00:00" sold_out="false">
            <zone zone_id="40" capacity="200" price="20.00" name="Platea" numbered="true" />
            <zone zone_id="38" capacity="0" price="15.00" name="Grada 2" numbered="false" />
            <zone zone_id="30" capacity="80" price="30.00" name="A28" numbered="true" />
         </event>
      </base_event>
      <base_event base_event_id="1591" sell_mode="online" organizer_company_id="1" title="Los Morancos">
         <event event_start_date="2021-07-31T20:00:00" event_end_date="2021-07-31T21:00:00" event_id="1642" sell_from="2021-06-26T00:00:00" sell_to="2021-07-31T19:50:00" sold_out="false">
            <zone zone_id="186" capacity="0" price="75.00" name="Amfiteatre" numbered="true" />
            <zone zone_id="186" capacity="12" price="65.00" name="Amfiteatre" numbered="false" />
         </event>
      </base_event>
      <base_event base_event_id="444" sell_mode="offline" organizer_company_id="1" title="Tributo a Juanito Valderrama">
         <event event_start_date="2021-09-31T20:00:00" event_end_date="2021-09-31T20:00:00" event_id="1642" sell_from="2021-02-10T00:00:00" sell_to="2021-09-31T19:50:00" sold_out="false">
            <zone zone_id="7" capacity="22" price="65.00" name="Amfiteatre" numbered="false" />
         </event>
      </base_event>
   </output>
</eventList>
"""


@app.route("/")
def index():
    return redirect("/api/v1/events/")


@app.route("/api/v1/events/", methods=["GET"])
def get_events_1():
    return Response(xml_data_1, mimetype="text/xml")


@app.route("/api/v2/events/", methods=["GET"])
def get_events_2():
    return Response(xml_data_2, mimetype="text/xml")


@app.route("/api/v3/events/", methods=["GET"])
def get_events_3():
    return Response(xml_data_3, mimetype="text/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
