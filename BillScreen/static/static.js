function preLoad() {
    baseGraph = new Image; baseGraph.src = '../static/forecastImg.svg';
    futureMinGraph = new Image; futureMinGraph.src = '../static/futureForecastImg.svg';
}
function changeIm(image) {
    document.getElementById('forecastGraph').src = eval(image + ".src")
}