$(document).ready(function () {
    var player1Name = localStorage.getItem("player1Name");
    var player2Name = localStorage.getItem("player2Name");

    console.log("Player 1 Name: ", player1Name);

    $("#player1Name").text(player1Name);
    $("#player2Name").text(player2Name);
    $("#playerTurn").text(player1Name);

    $.ajax({
        type: "POST",
        url: "/initializeGame",
        dataType: "text",
        success: function (response) {
            document.getElementById("svg-container").innerHTML = response;

            // Now that the SVG is loaded, select it
            let tableSVG = document.querySelector("#svg-container svg");

            // Make sure svgElement is not null
            if (!tableSVG) {
                console.error("SVG Element not found!");
                return;
            }

            setupEventListeners(tableSVG); // Call a function to setup event listeners
            displayCueLine();
        },
        error: function () {
            console.error("Error initializing game");
        },
    });
});

// Global Variables

let isDragging = false;

function displayCueLine() {
    let cueBall = $("#cue_ball");

    let cueBallX = parseFloat(cueBall.attr("cx"));
    let cueBallY = parseFloat(cueBall.attr("cy"));
    let aimLineY = 0;
    let cueLineY = 0;

    // Check if the cue ball is above the center of the table
    if (cueBallY < 1375) {
        aimLineY = cueBallY + 56; // Move cue line above the cue ball
        cueLineY = cueBallY - 56; // Move cue line below the cue ball

    } else {
        aimLineY = cueBallY - 56; // Move cue line below the cue ball
        cueLineY = cueBallY + 56; // Move cue line above the cue ball
    }

    // Length of the cue line
    let cueLineLength = 500;
    let aimLineLength = 2200;

    // Select the SVG container where you want to append the line
    let svg = $("#svg-container svg")[0];

    // Create a new SVG cueline element
    let cue_line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    cue_line.setAttribute("id", "pool_cue");
    cue_line.setAttribute("class", "cue_line");
    cue_line.setAttribute("x1", cueBallX);
    cue_line.setAttribute("y1", cueLineY);
    cue_line.setAttribute("x2", cueBallX); // Set x2 based on desired length from cue ball position
    cue_line.setAttribute("y2", cueLineY + cueLineLength); // Keep y2 the same as y1 initially
    cue_line.setAttribute("stroke", "black");
    cue_line.setAttribute("stroke-width", "25");
    cue_line.setAttribute("visibility", "visible");

    // Create a new SVG aimline element
    let aim_line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    // checkLinePath()
    aim_line.setAttribute("class", "cue_line");
    aim_line.setAttribute("id", "aim_line");
    aim_line.setAttribute("x1", cueBallX);
    aim_line.setAttribute("y1", aimLineY);
    aim_line.setAttribute("x2", cueBallX); // Set x2 based on desired length from cue ball position
    aim_line.setAttribute("y2", aimLineY - aimLineLength); // Keep y2 the same as y1 initially
    aim_line.setAttribute("length", aimLineLength);
    aim_line.setAttribute("stroke", "grey");
    aim_line.setAttribute("stroke-width", "10");
    aim_line.setAttribute("visibility", "visible");

    // Append the line to the SVG container
    svg.appendChild(cue_line);
    svg.appendChild(aim_line);
}

function rotatePoolCue(angle) {

    let cueBall = $("#cue_ball");
    let cueBallX = parseFloat(cueBall.attr("cx"));
    let cueBallY = parseFloat(cueBall.attr("cy"));

    // Lengths of the cue line and aim line
    let poolCueLength = 500;
    let aimLineLength = 2200;

    // Calculate new coordinates for cue line
    let cueLineEndX = cueBallX * Math.cos(angle);
    let cueLineEndY = cueBallY * Math.sin(angle);

    // Calculate new coordinates for aim line
    let aimLineEndX = cueBallX * Math.cos(angle);
    let aimLineEndY = cueBallY * Math.sin(angle);

    // Update the cue line's position
    $("#pool_cue")
        .attr("x1", cueBallX)
        .attr("y1", cueBallY)
        .attr("x2", cueLineEndX)
        .attr("y2", cueLineEndY + poolCueLength);

    // Update the aim line's position
    $("#aim_line")
        .attr("x1", cueBallX)
        .attr("y1", cueBallY)
        .attr("x2", aimLineEndX)
        .attr("y2", aimLineEndY - aimLineLength);

    checkLinePath();
}


function checkLinePath() {
    const balls = $(".ball");
    const aimLine = $("#aim_line");

    let x1 = parseFloat(aimLine.attr("x1"));
    let y1 = parseFloat(aimLine.attr("y1"));
    let x2 = parseFloat(aimLine.attr("x2"));
    let y2 = parseFloat(aimLine.attr("y2"));

    balls.each(function () {
        let ball = $(this);
        let ballX = parseFloat(ball.attr("cx"));
        let ballY = parseFloat(ball.attr("cy"));
        let ballRadius = parseFloat(ball.attr("r"));

        if (lineIntersectsCircle(x1, y1, x2, y2, ballX, ballY, ballRadius)) {
            console.log(`Ball at (${ballX}, ${ballY}) intersects with the aim line.`);
        }
    });
}

function lineIntersectsCircle(x1, y1, x2, y2, cx, cy, r) {
    // Line segment from (x1, y1) to (x2, y2)
    let dx = x2 - x1;
    let dy = y2 - y1;

    // Vector from (x1, y1) to the circle center (cx, cy)
    let fx = x1 - cx;
    let fy = y1 - cy;

    let a = dx * dx + dy * dy;
    let b = 2 * (fx * dx + fy * dy);
    let c = (fx * fx + fy * fy) - r * r;

    let discriminant = b * b - 4 * a * c;

    if (discriminant >= 0) {
        discriminant = Math.sqrt(discriminant);

        let t1 = (-b - discriminant) / (2 * a);
        let t2 = (-b + discriminant) / (2 * a);

        if ((t1 >= 0 && t1 <= 1) || (t2 >= 0 && t2 <= 1)) {
            return true;
        }
    }
    return false;
}

function calculateAngle(x1, y1, x2, y2) {
    return Math.atan2(y2 - y1, x2 - x1);
}

function getCueAngle() {
    const cue = $(".cue_line");

    const transform = cue.attr("transform");
    if (transform) {
        const match = /rotate\(([^)]+)\)/.exec(transform);
        if (match) {
            const angle = parseFloat(match[1]);
            return angle * (Math.PI / 180); // Convert degrees to radians
        }
    }
    return 0;
}

function setupEventListeners(tableSVG) {
    let isDragging = false;
    let initialMouseAngle;
    let initialCueAngle;

    let cueBall = $("#cue_ball");

    $("#svg-container svg").on("mousedown", "#pool_cue", function (e) {
        let svg = document.querySelector("#svg-container svg");
        let svgPoint = getSVGCoordinates(svg, e);
        let mouseX = svgPoint.x;
        let mouseY = svgPoint.y;

        isDragging = true;
        initialMouseAngle = calculateAngle(parseFloat(cueBall.attr("cx")), parseFloat(cueBall.attr("cy")), mouseX, mouseY);
        initialCueAngle = getCueAngle();
    });

    $("#svg-container svg").on("mousemove", function (e) {
        if (isDragging) {

            let svg = document.querySelector("#svg-container svg");
            let svgPoint = getSVGCoordinates(svg, e);
            let mouseX = svgPoint.x;
            let mouseY = svgPoint.y;

            // console.log("Mouse Move Coordinates:", mouseX, mouseY); // Debugging log

            // const dx = mouseX - cueBallX;
            // const dy = mouseY - cueBallY;

            const currentMouseAngle = calculateAngle(
                parseFloat(cueBall.attr("cx")),
                parseFloat(cueBall.attr("cy")),
                mouseX,
                mouseY
            );
            
            const angle = initialCueAngle + (currentMouseAngle - initialMouseAngle);
            
            rotatePoolCue(angle);
        }
    });

    $("#svg-container svg").on("mouseup", function (e) {
        isDragging = false;
    });

    $("#svg-container svg").on("mouseleave", function (e) {
        isDragging = false;
    });

    // $("#svg-container").on("mousedown", "#cue_ball", function (e) {
    //     e.preventDefault();
    //     isDragging = true;

    //     // Assuming the cue ball's center is stored in its 'cx' and 'cy' attributes
    //     let ballCenterX = parseFloat($(this).attr("cx"));
    //     let ballCenterY = parseFloat($(this).attr("cy"));

    //     initialPosition = { x: ballCenterX, y: ballCenterY };

    //     let cueLine = $(".cue_line");
    //     if (cueLine.length === 0) {
    //         let svg = $("#svg-container svg")[0]; // Assuming there's only one SVG element inside #svg-container
    //         let line = document.createElementNS(
    //             "http://www.w3.org/2000/svg",
    //             "line"
    //         );
    //         line.setAttribute("id", "cue_line");
    //         line.setAttribute("x1", initialPosition.x);
    //         line.setAttribute("y1", initialPosition.y);
    //         line.setAttribute("x2", initialPosition.x); // Initial x2, y2 set to the same as x1, y1
    //         line.setAttribute("y2", initialPosition.y);
    //         line.setAttribute("stroke", "black");
    //         line.setAttribute("stroke-width", "8"); // Adjusted for visibility
    //         line.setAttribute("visibility", "visible");
    //         svg.appendChild(line);
    //     } else {
    //         cueLine.attr({
    //             x1: initialPosition.x,
    //             y1: initialPosition.y,
    //             x2: initialPosition.x, // Reset x2, y2 on new mousedown
    //             y2: initialPosition.y,
    //             visibility: "visible",
    //         });
    //     }
    // });

    // $("#svg-container").on("mousemove", function (e) {
    //     if (!isDragging) return;

    //     let svg = document.querySelector("#svg-container svg");
    //     let svgPoint = getSVGCoordinates(svg, e);

    //     // Update line's end point to the mouse position
    //     $(".cue_line").attr({
    //         x2: svgPoint.x,
    //         y2: svgPoint.y,
    //     });
    // });

    function displayNextSVG(svgArray) {
        let currentIndex = 0; // Start from the first SVG
        console.log("Received SVG data: ", svgArray[currentIndex]);

        function updateSVG() {
            if (currentIndex < svgArray.length) {
                $("#svg-container").html(svgArray[currentIndex]); // Update the SVG container
                currentIndex++; // Move to the next SVG
                setTimeout(updateSVG, 10); // Wait for 0.01s before displaying the next SVG
            }
        }

        updateSVG(); // Start the SVG update loop
    }

    // $(document).on("mouseup", function (e) {
    //     if (isDragging) {
    //         // changeTurn();

    //         const svgPoint = getSVGCoordinates(svgElement, e);
    //         isDragging = false;
    //         $(".cue_line").attr("visibility", "hidden");
    //         console.log(
    //             `Dragged from (${initialPosition.x}, ${initialPosition.y}) to (${svgPoint.x}, ${svgPoint.y})`
    //         );

    //         // Prepare the data
    //         const dataToSend = {
    //             initialPosition: {
    //                 x: initialPosition.x,
    //                 y: initialPosition.y,
    //             },
    //             svgPoint: {
    //                 x: svgPoint.x,
    //                 y: svgPoint.y,
    //             },
    //         };

    //         // Send the data using AJAX
    //         $.ajax({
    //             type: "POST",
    //             url: "/processDrag", // This URL should match your server endpoint
    //             contentType: "application/json",
    //             data: JSON.stringify(dataToSend),
    //             success: function (response) {
    //                 // Assuming the response is already parsed into an object
    //                 let svgData = response.svgData; // Get the SVG data from the response
    //                 let svgArray = Object.values(svgData); // Convert SVG data object to an array

    //                 console.log("Received SVG data: ");

    //                 displayNextSVG(svgArray); // Call the function to display SVGs one by one
    //                 displayCueLine();
    //             },
    //             error: function (xhr, status, error) {
    //                 console.error("Error sending data:", error);
    //             },
    //         });
    //     }
    // });

    function getSVGCoordinates(svg, event) {
        var pt = svg.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        return pt.matrixTransform(svg.getScreenCTM().inverse());
    }

    function changeTurn() {
        var spanText = $("#playerTurn").text();

        var player1Name = localStorage.getItem("player1Name");
        var player2Name = localStorage.getItem("player2Name");

        if (spanText === player1Name) {
            $("#playerTurn").text(player2Name);
        } else {
            $("#playerTurn").text(player1Name);
        }
    }
}
