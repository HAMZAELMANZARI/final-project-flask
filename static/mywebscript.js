let RunSentimentAnalysis = () => {
    const textToAnalyze = document.getElementById("textToAnalyze").value;

    if (!textToAnalyze.trim()) {
        document.getElementById("system_response").innerHTML = "Text is blank. Please provide a non-empty text.";
        return;
    }

    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) {
                document.getElementById("system_response").innerHTML = xhttp.responseText;
            } else {
                document.getElementById("system_response").innerHTML = xhttp.responseText || "An error occurred.";
            }
        }
    };
    xhttp.open("GET", "emotionDetector?textToAnalyze=" + encodeURIComponent(textToAnalyze), true);
    xhttp.send();
};
