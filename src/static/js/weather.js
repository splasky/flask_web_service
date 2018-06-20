"use strict";

// For some reasons I don't know, geolocation api didn't work sometimes
// location can't be retrieved mostly
// so I made it manually, you key in your zipcode/city name/latitude/longitude
// then you are good to go!

// ====================================
//       code by: Ben Bright
//       date: August, 2017
// =====================================

window.onload = function() {
  // weatherApp component
  Vue.component("weather-app", {
    template: `<div class="card bg-light mb-3">
    <div class="card-body">
        <div class="weather">
            <div class="top-section">
                <p>{{ city }},
                    <span>{{ location }}</span>
                </p>
                <div>
                    <p>{{ day }}, {{ hours }}:{{ mins }} {{ hours
                        < 12 ? "AM " : "PM " }}</p>
                            <p>{{ cloudtxt }}</p>
                </div>
            </div>
            <div class="bottom-section ">
                <div class="bottom-left ">
                    <p>
                        <img :src="cloudicon " height="50 " alt="cloud ">
                    </p>
                    <p>{{ temps === true ? tempcelsius_min : tempfahrt_min }}</p>
                    <p>~</p>
                    <p>{{ temps === true ? tempcelsius_max : tempfahrt_max }}</p>
                    <div>
                        <span @click="temps=true " :class="{ 'temp-c': temps} ">
                            <sup> o</sup>C</span>
                        <span>|</span>
                        <span @click="temps=false " :class="{ 'temp-f': !temps} ">
                            <sup> o</sup>F</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>`,

    // props to recieve data from parent vue instance object
    props: [
      "city",
      "temp",
      "tempc_max",
      "tempc_min",
      "tempf_max",
      "tempf_min",
      "cloudtxt",
      "cloudicon",
      "location",
      "hours",
      "day",
      "mins"
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
  var fetch_weather = new Vue({
    el: "#app",
    data: {
      posts: [],
      validResponse: "",
      city: "臺中市",
      temp:true,
    },
    methods: {
      fetchData(city) {
        let self = this;
        let date = new Date().getDay();

        if (city !== null) {
          self.city = city;
        }
        let location = self.city;
        if (location === null) {
          console.log("Cancelled request...try again!");
          return;
        } else {
          axios
            .get("/week_weather_from_city", {
              params: {
                city: location
              }
            })
            .then(function(response) {
              if (response.statusText !== "OK") {
                self.validResponse = false;
              } else {
                self.validResponse = true;
                let data = response.data;
                // obtain city name, country, temperature, cloud icon,
                //  cloud info from api
                let city = data.location.name;
                let country = data.location.country;
                let temp = self.temp;
                let date = new Date();
                let i =0;

                for (let index in data.current) {
                  let current_date = fetch_weather.get_day_and_hours(date);
                  let obj = data.current[index];
                  let post = {
                    city: city,
                    country: country,
                    temp: temp,
                    max_temp_c: obj.max_temp_c,
                    max_temp_f: obj.max_temp_f,
                    min_temp_c: obj.min_temp_c,
                    min_temp_f: obj.min_temp_f,
                    conditionText: obj.condition.text,
                    conditionIcon: "http:" + obj.condition.icon,
                    validResponse: self.validResponse,
                    hours: current_date.hours,
                    mins: current_date.mins,
                    day: current_date.day
                  };

                  date.setDate(date.getDate() + 1);
                  self.posts.push(post);
                  i+=1;
                  if(i>6){
                      break;
                  }
                }
              }
            })
            .catch(function(error) {
              console.log(`Bad Request: ${error}`);
            });
        }
      },
      get_day_and_hours(date) {
        // get hours from api
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

        return {
          hours: hours,
          mins: mins,
          day: day
        };
      }
    }
  });
  var city_weather = new Vue({
    el: "#city_for_weather",
    data: {
      weather_city: "臺中市"
    },
    watch: {
      weather_city() {
        fetch_weather.fetchData(this.weather_city);
      }
    },
    mounted: function() {
        this.weather_city = "臺中市";
    }
  });
};
