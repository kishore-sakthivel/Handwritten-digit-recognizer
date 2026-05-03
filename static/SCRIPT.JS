const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const predictBtn = document.getElementById("predict");
const clearBtn = document.getElementById("clear");
const saveBtn = document.getElementById("save");

const result = document.getElementById("result");

// =========================
// CANVAS SETTINGS
// =========================

ctx.fillStyle = "black";
ctx.fillRect(0, 0, canvas.width, canvas.height);

ctx.lineWidth = 18;
ctx.strokeStyle = "white";
ctx.lineCap = "round";
ctx.lineJoin = "round";

let drawing = false;

// =========================
// MOUSE EVENTS
// =========================

canvas.addEventListener("mousedown", start);
canvas.addEventListener("mouseup", stop);
canvas.addEventListener("mouseleave", stop);
canvas.addEventListener("mousemove", draw);

// =========================
// TOUCH EVENTS (MOBILE)
// =========================

canvas.addEventListener("touchstart", (e) => {
    e.preventDefault();

    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();

    start({
        offsetX: touch.clientX - rect.left,
        offsetY: touch.clientY - rect.top
    });
});

canvas.addEventListener("touchmove", (e) => {
    e.preventDefault();

    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();

    draw({
        offsetX: touch.clientX - rect.left,
        offsetY: touch.clientY - rect.top
    });
});

canvas.addEventListener("touchend", stop);

// =========================
// DRAW FUNCTIONS
// =========================

function start(e){

    drawing = true;

    ctx.beginPath();

    ctx.moveTo(
        e.offsetX,
        e.offsetY
    );
}

function stop(){

    drawing = false;

    ctx.beginPath();
}

function draw(e){

    if(!drawing) return;

    ctx.lineTo(
        e.offsetX,
        e.offsetY
    );

    ctx.stroke();

    ctx.beginPath();

    ctx.moveTo(
        e.offsetX,
        e.offsetY
    );
}

// =========================
// CLEAR BUTTON
// =========================

clearBtn.onclick = () => {

    ctx.fillStyle = "black";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    result.innerHTML = "-";

    const oldChart = document.getElementById("probChart");

    if(oldChart){
        oldChart.remove();
    }
}

// =========================
// PREDICT BUTTON
// =========================

predictBtn.onclick = async () => {

    const image = canvas.toDataURL();

    const response = await fetch("/predict", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            image
        })
    });

    const data = await response.json();

    // =========================
    // SHOW RESULT
    // =========================

    result.innerHTML = `
        <div class="big-digit">
            ${data.digit}
        </div>

        <div class="confidence">
            Confidence: ${data.confidence}%
        </div>
    `;

    // =========================
    // REMOVE OLD CHART
    // =========================

    const oldChart = document.getElementById("probChart");

    if(oldChart){
        oldChart.remove();
    }

    // =========================
    // CREATE CHART CANVAS
    // =========================

    const chartCanvas = document.createElement("canvas");

    chartCanvas.id = "probChart";

    document
        .querySelector(".container")
        .appendChild(chartCanvas);

    // =========================
    // CREATE BAR CHART
    // =========================

    new Chart(chartCanvas, {

        type: "bar",

        data: {

            labels: [
                '0','1','2','3','4',
                '5','6','7','8','9'
            ],

            datasets: [{

                label: "Probability %",

                data: data.probabilities
            }]
        },

        options: {

            responsive: true,

            scales: {

                y: {

                    beginAtZero: true,

                    max: 100
                }
            }
        }
    });
}

// =========================
// SAVE DATASET BUTTON
// =========================

saveBtn.onclick = async () => {

    let digit = prompt(
        "Enter correct digit (0-9)"
    );

    if(digit === null) return;

    const image = canvas.toDataURL();

    await fetch("/save_dataset", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            image,
            label: digit
        })
    });

    alert("Saved Successfully");
}