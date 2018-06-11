"use strict";

// For some reasons I don't know, geolocation api didn't work sometimes
// location can't be retrieved mostly
// so I made it manually, you key in your zipcode/city name/latitude/longitude
// then you are good to go!

// ====================================
//       code by: Ben Bright
//       date: August, 2017
// =====================================


window.onload = function () {

    // weatherApp component
    Vue.component("weather-app", {
        template: `<div class="wrapper">
            <div class="weather">
                <div class="top-section">
                    <p>{{ city }}, <span>{{ location }}</span></p>
                    <div>
                        <p>{{ day }}, {{ hours }}:{{ mins }} {{ hours < 12 ? "AM" : "PM" }}</p>
                        <p>{{ cloudtxt }}</p>
                    </div>
                </div>
                <div class="bottom-section">
                    <div class="bottom-left">
                        <p><img :src="cloudicon" height="50" alt="cloud"></p>
                        <p>{{ temps === true ? tempcelsius_min : tempfahrt_min }}</p>
                        <p>~</p>
                        <p>{{ temps === true ? tempcelsius_max : tempfahrt_max }}</p>
                        <div>
                            <span @click="temps = true" :class="{'temp-c': temps}"><sup> o</sup>C</span>
                            <span>|</span>
                            <span @click="temps = false" :class="{'temp-f': !temps}"><sup> o</sup>F</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>`,

        // props to recieve data from parent vue instance object
        props: [
            "city", "temp", "tempc_max", "tempc_min","tempf_max","tempf_min",
            "cloudtxt", "cloudicon","location",
            "hours", "day", "mins"
        ],

        // component data properties
        data() {
            return {
                tempcelsius_max: this.tempc_max,
                tempcelsius_min: this.tempc_min,
                tempfahrt_max: this.tempf_max,
                tempfahrt_min: this.tempf_min,
                temps: this.temp
            };
        }
    });

    // Vue instance object
    var fetch_weather=new Vue({
        el: "#app",
        data: {
            city: "臺中市",
            location: "台灣",
            hours: 0,
            mins: 0,
            day: "",
            temp: true,
            max_temp_c:"",
            max_temp_f:"",
            min_temp_c:"",
            min_temp_f:"",
            conditionText: "",
            conditionIcon: "http:",
            validResponse: ""
        },

        created() {
            this.fetchData();
        },

        methods: {
            fetchData(city) {
                let self = this;
                let date=new Date().getDay();

                if (city!==null){
                    self.city=city
                }
                let location = self.city;
                if (location === null) {
                    console.log("Cancelled request...try again!");
                    return;
                } else {
                    axios.get("/weather_from_city",{
                            params:{
                                city:location,
                                date:date
                            }
                    }).then(function (response) {
                            if (response.statusText !== "OK") {
                                self.validResponse = false;
                            } else {
                                self.validResponse = true;

                                // obtain city name, country, temperature, cloud icon, 
                                //  cloud info from api
                                self.city = response.data.location.name;
                                self.max_temp_c = Math.floor(response.data.current.max_temp_c);
                                self.max_temp_f = Math.floor(response.data.current.max_temp_f);
                                self.min_temp_c = Math.floor(response.data.current.min_temp_c);
                                self.min_temp_f = Math.floor(response.data.current.min_temp_f);
                                self.conditionText = response.data.current.condition.text;
                                self.conditionIcon += response.data.current.condition.icon;
                                self.location = response.data.location.country;

                                // get hours from api
                                let date = new Date();
                                self.hours = date.getHours();

                                // format time minutes
                                if (date.getMinutes() < 10) {
                                    self.mins = "0" + date.getMinutes();
                                } else {
                                    self.mins = date.getMinutes();
                                }

                                // format day of week
                                let days = ["Sun", "Mon", "Tue", "Wed", "Thur", "Fri", "Sat"];

                                for (let i = 0; i < days.length; i++) {
                                    if (date.getDay() === i) {
                                        self.day = days[i];
                                    }
                                }
                            }
                        })
                        .catch(function (error) {
                            console.log(`Bad Request: ${error}`);
                    });
                }
            }
        }
    });
    var city_weather=new Vue({
      el: '#city_for_weather',
      data: {
        weather_city:'' 
      },
        watch:{
            weather_city(){
                fetch_weather.fetchData(this.weather_city);
            }
        }
    });
};


