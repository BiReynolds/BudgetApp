function preLoad() {
    next30Graph = new Image; next30Graph.src = '../static/next30.svg'
    next90Graph = new Image; next90Graph.src = '../static/next90.svg'
    baseGraph = new Image; baseGraph.src = '../static/forecastImg.svg';
    futureMinGraph = new Image; futureMinGraph.src = '../static/futureForecastImg.svg';
    document.getElementById('image-select').addEventListener("change", updateIm);
}
function updateIm() {
    image = document.getElementById('image-select').selectedOptions[0].value
    document.getElementById('forecastGraph').src = eval(image + ".src")
}
