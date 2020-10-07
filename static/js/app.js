/*
  HELPERS
*/

function average(arr) {
  let sum = arr.reduce((memo, num) => {
    return memo + num;
  }, 0);
  return sum / (arr.length === 0 ? 1 : arr.length);
}

function roundTenths(num) {
  return Math.round(num * 10) / 10;
}

function roundHundreths(num) {
  return Math.round(num * 100) / 100;
}

function roundHalf(num) {
  return Math.round(num * 2) / 2;
}

function degToCompass(num) {
  let val = Math.floor(num / 22.5 + 0.5),
  dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  return dirs[val % 16];
}

/*
    APP
  */
const corsProxy = 'https://cors-anywhere.herokuapp.com/';
const breakOptions = [
{
  id: '5538',
  name: 'Ala Moana',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/5538?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '4756',
  name: 'Chuns',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/4756?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '10845',
  name: 'Makaha',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/10845?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '5540',
  name: 'Makapuu Beach',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/5540?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '10838',
  name: 'Popoia Island',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/10838?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '5533',
  name: 'Populars',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/5533?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '10837',
  name: 'Sandys Beach Park',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/10837?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '4746',
  name: 'Sunset',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/4746?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

// {
//   id: null,
//   name: '–––',
//   url: null
// },
{
  id: '5015',
  name: 'Fort Point',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/5015?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '4127',
  name: 'Ocean Beach',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/4127?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '5013',
  name: 'Pacifica',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/5013?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' },

{
  id: '5090',
  name: 'Stinson Beach',
  url: corsProxy + 'https://api.surfline.com/v1/forecasts/5090?resources=surf,wind,tide,weather&days=1&getAllSpots=false&units=e&interpolate=false&showOptimal=false' }];



let mapScript = document.createElement('script');
mapScript.type = 'text/javascript';
mapScript.src = '//maps.googleapis.com/maps/api/js?key=AIzaSyDsIY-GESpfBfIGFHnpcmzcBZkhSPThyto';
mapScript.defer = true;
mapScript.async = true;
let s = document.getElementsByTagName('script')[0];
s.parentNode.insertBefore(mapScript, s);

let report = new Vue({
  el: '#report',
  data: {
    isActive: false,
    isLoading: false,
    subtitle: 'Choose a surf break below',
    surfBreaks: breakOptions,
    activeSurfBreak: breakOptions[0],
    current: '',
    min: '',
    max: '',
    location: {
      lat: '',
      lng: '' },

    swells: [],
    wind: {
      speed: '',
      direction: '' },

    sun: {
      rise: '',
      set: '' },

    tide: {
      graph: '',
      data: '',
      extremes: [] },

    temperature: {
      min: '',
      max: '' } },


  created: function () {
    this.setWidth();
  },
  mounted: function () {
    this.isActive = true;
    this.getSurf(breakOptions[0]);
  },
  computed: {
    surfRange: function () {
      return this.min + ' - ' + this.max + '<span>ft</span>';
    },
    sunRange: function () {
      return this.sun.rise + ' - ' + this.sun.set;
    },
    tempRange: function () {
      return this.temperature.min + ' - ' + this.temperature.max;
    } },

  watch: {
    current: function (selection) {
      if (!selection.id) return;
      if (!this.isActive) this.isActive = true;

      this.getSurf(selection);
    } },

  methods: {
    setWidth: function () {
      let locationList = document.querySelector('.locations__container'),
      firstEl = document.querySelectorAll('.locations__option')[0],
      titleLeft = document.querySelector('.header__title').getBoundingClientRect().left,
      width = firstEl.getBoundingClientRect().width + parseInt(window.getComputedStyle(firstEl)['margin-right']),
      count = this.surfBreaks.length;

      locationList.style.paddingLeft = `${titleLeft}px`;
      locationList.style.paddingRight = `${titleLeft}px`;
      locationList.style.width = `${count * width + titleLeft * 2}px`;
    },
    getSurf: function (selection) {
      this.isLoading = true;
      this.activeSurfBreak = selection;

      axios.get(selection.url).
      then(response => {
        this.isLoading = false;
        let result = {
          date: response.data.Surf.startDate_pretty_LOCAL,
          surfMax: response.data.Surf.surf_max[0],
          surfMin: response.data.Surf.surf_min[0],
          location: {
            longitude: response.data.lon,
            latitude: response.data.lat },

          swells: [
          {
            angle: response.data.Surf.swell_direction1[0],
            height: response.data.Surf.spot.swell_height1[0],
            period: response.data.Surf.spot.swell_period1[0] },

          {
            angle: response.data.Surf.swell_direction2[0],
            height: response.data.Surf.spot.swell_height2[0],
            period: response.data.Surf.spot.swell_period2[0] },

          {
            angle: response.data.Surf.swell_direction3[0],
            height: response.data.Surf.spot.swell_height3[0],
            period: response.data.Surf.spot.swell_period3[0] }],


          sun: {
            rise: response.data.Tide.SunPoints[0].Rawtime,
            set: response.data.Tide.SunPoints[1].Rawtime },

          temperature: {
            min: response.data.Weather.temp_min,
            max: response.data.Weather.temp_max },

          tide: {
            data: response.data.Tide.dataPoints,
            extremes: response.data.Tide.dataPoints },

          wind: {
            speed: response.data.Wind.wind_speed[0],
            angle: response.data.Wind.wind_direction[0] } };



        this.subtitle = 'Actual data from ' + moment(result.date, 'MMMM DD, YYYY kk:mm:ss').format('M/D/YYYY');

        this.max = average(result.surfMax) < .5 ? 'flat' : roundHalf(average(result.surfMax));
        this.min = average(result.surfMin) < .5 ? 'flat' : roundHalf(average(result.surfMin));

        this.location.lng = result.location.longitude;
        this.location.lat = result.location.latitude;
        this.buildMap(this.location.lat, this.location.lng);

        result.swells.forEach((obj, index) => {
          this.swells[index] = {
            angle: average(result.swells[index].angle),
            direction: degToCompass(average(result.swells[index].angle)),
            height: roundTenths(average(result.swells[index].height)),
            period: roundTenths(average(result.swells[index].period)) };

        });

        this.sun.rise = moment(result.sun.rise, 'MMMM DD, YYYY HH:mm:ss').format('h:mma');
        this.sun.set = moment(result.sun.set, 'MMMM DD, YYYY HH:mm:ss').format('h:mma');

        this.temperature.min = roundTenths(average(result.temperature.min));
        this.temperature.max = roundTenths(average(result.temperature.max));

        this.tide.data = result.tide.data.
        filter(dataPoint => dataPoint.type == 'NORMAL').
        filter(dataPoint => {
          let dataTime = moment(dataPoint.Rawtime, 'MMMM DD, YYYY HH:mm:ss').format('MM/DD'),
          startTime = moment(result.tide.data[0].Rawtime, 'MMMM DD, YYYY HH:mm:ss').format('MM/DD');
          return dataTime === startTime;
        }).
        map(dataPoint => {
          return {
            time: moment(dataPoint.Rawtime, 'MMMM DD, YYYY HH:mm:ss').format('h:mma'),
            height: dataPoint.height };

        });
        this.buildTide(this.tide.data);
        this.tide.extremes = result.tide.data.
        filter(dataPoint => dataPoint.type == 'High' || dataPoint.type == 'Low').
        filter(dataPoint => {
          let dataTime = moment(dataPoint.Rawtime, 'MMMM DD, YYYY HH:mm:ss').format('MM/DD'),
          startTime = moment(result.tide.data[0].Rawtime, 'MMMM DD, YYYY HH:mm:ss').format('MM/DD');
          return dataTime === startTime;
        }).
        map(dataPoint => {
          return {
            time: moment(dataPoint.Rawtime, 'MMMM DD, YYYY HH:mm:ss').format('h:mma'),
            height: dataPoint.height,
            type: dataPoint.type };

        });

        this.wind.speed = Math.round(average(result.wind.speed));
        this.wind.direction = degToCompass(average(result.wind.angle));
      }).
      catch(error => {
        this.isLoading = false;
        console.error(error);
      });
    },
    buildMap: function (lat, lng) {
      this.center = { lat: parseFloat(lat), lng: parseFloat(lng) };

      if (this.map) {
        this.map.panTo(this.center);
        return;
      }

      this.map = new google.maps.Map(document.querySelector('.map'), {
        center: this.center,
        zoom: 10,
        disableDefaultUI: true,
        styles: [{ "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#313E51" }] }, { "featureType": "landscape", "elementType": "geometry", "stylers": [{ "color": "#313E51" }, { "lightness": -25 }] }, { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#313E51" }, { "lightness": -40 }] }, { "featureType": "poi", "elementType": "geometry", "stylers": [{ "visibility": "off" }] }, { "featureType": "transit", "elementType": "geometry", "stylers": [{ "visibility": "off" }] }, { "elementType": "labels.text.stroke", "stylers": [{ "visibility": "off" }] }, { "elementType": "labels.text.fill", "stylers": [{ "visibility": "off" }] }, { "featureType": "administrative", "elementType": "geometry", "stylers": [{ "visibility": "off" }] }, { "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] }, { "featureType": "poi.park", "elementType": "geometry", "stylers": [{ "visibility": "off" }] }] });


      window.addEventListener('resize', () => {
        this.map.panTo(this.center);
      }, true);
    },
    buildTide: function (data) {
      let margin = { top: 0, right: 0, bottom: 0, left: 0 },
      width = 400,
      widthBar = width / data.length,
      height = 150,
      graph = d3.select('#tide-graph');

      const HEIGHTS = d3.set(data, d => {
        return d.height;
      }),
      TIMES = d3.set(data, d => {
        return d.time;
      }),
      EXTENT_TIMES = d3.extent(TIMES.values(), d => {
        return d;
      }),
      EXTENT_HEIGHTS = d3.extent(HEIGHTS.values(), d => {
        return d;
      }),
      X_SCALE = d3.scaleTime().
      domain([EXTENT_TIMES[0], EXTENT_TIMES[1]]).
      range([0, width]),
      Y_SCALE = d3.scaleLinear().
      domain([0, Math.ceil(EXTENT_HEIGHTS[1])]).
      range([height / 10, height]);

      if (!graph.select('svg').nodes().length) {
        graph.
        append('svg').
        attr('viewBox', `0 0 ${width} ${height}`).
        attr('preserveAspectRatio', 'xMidYMid meet');
      } else {
        graph.
        selectAll('rect').
        remove();
      }

      graph.select('svg').
      selectAll('rect').
      data(data).
      enter().
      append('rect').
      on('mouseover', function (d, i, elements) {
        let thisNode = d3.select(this),
        thisHeight = roundTenths(d.height),
        thisTime = d.time;

        graph.select('svg').
        append('text').
        attr('x', 8).
        attr('y', height - 8).
        html(thisHeight + '’ @ ' + thisTime);

        d3.selectAll(elements).
        filter(':not(:hover)').
        style('fill-opacity', .5);
      }).
      on('mouseout', function (d, i, elements) {
        d3.selectAll(elements).
        style('fill-opacity', 1);

        graph.selectAll('text').
        remove();
      }).
      attr('width', widthBar - widthBar / 2).
      attr('x', (d, i) => i * widthBar + widthBar / 4).
      attr('y', height).
      attr('ry', widthBar / 4).
      attr('rx', widthBar / 4).
      transition().
      duration(500).
      attr('height', d => {
        return Y_SCALE(d.height);
      }).
      attr('y', d => {
        return height - Y_SCALE(d.height);
      });


    } } });