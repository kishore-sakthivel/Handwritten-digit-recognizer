const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const predictBtn = document.getElementById("predict");
const clearBtn = document.getElementById("clear");
const saveBtn = document.getElementById("save");

const result = document.getElementById("result");

ctx.fillStyle = "black";
ctx.fillRect(0,0,canvas.width,canvas.height);

ctx.lineWidth = 18;
ctx.lineCap = "round";
ctx.strokeStyle = "white";
ctx.lineCap = "round";
ctx.lineJoin = "round";

let drawing = false;

canvas.addEventListener("mousedown", start);
canvas.addEventListener("mouseup", stop);
canvas.addEventListener("mousemove", draw);

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

    ctx.lineTo(e.offsetX,e.offsetY);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(e.offsetX,e.offsetY);
}

clearBtn.onclick = () => {

    ctx.fillStyle = "black";
    ctx.fillRect(0,0,canvas.width,canvas.height);

    result.innerHTML = "-";
}

predictBtn.onclick = async () => {

    const image = canvas.toDataURL();

    const response = await fetch("/predict", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({image})
    });

    const data = await response.json();

    result.innerHTML = `${data.digit} (${data.confidence}%)`;
}

saveBtn.onclick = async () => {

    let digit = prompt("Enter correct digit (0-9)");

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

    alert("Saved");
}