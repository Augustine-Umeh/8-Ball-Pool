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

    if (cueBallY < 1375) {
        cueBallY -= 56; // Move cue line above the cue ball
    } else {
        cueBallY += 56; // Move cue line below the cue ball
    }

    // Length of the cue line
    let cueLineLength = 400;

    // Select the SVG container where you want to append the line
    let svg = $("#svg-container svg")[0];

    // Create a new SVG line element
    let line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("id", "cue_line");
    line.setAttribute("x1", cueBallX);
    line.setAttribute("y1", cueBallY);
    line.setAttribute("x2", cueBallX); // Set x2 based on desired length from cue ball position
    line.setAttribute("y2", cueBallY + cueLineLength); // Keep y2 the same as y1 initially
    line.setAttribute("stroke", "black");
    line.setAttribute("stroke-width", "25");
    line.setAttribute("visibility", "visible");

    // Append the line to the SVG container
    svg.appendChild(line);
}

function rotatePoolCue(angle) {
    let cueBall = $("#cue_ball");
    const poolCue = $("#cue_line");

    let cueBallX = parseFloat(cueBall.attr("cx"));
    let cueBallY = parseFloat(cueBall.attr("cy"));

    const angleDegrees = angle * (180 / Math.PI); // Convert angle to degrees

    console.log("Degree: ", angleDegrees);

    poolCue.attr("transform-origin", `${cueBallX} ${cueBallY}`);
    poolCue.attr("transform", `rotate(${angleDegrees})`);
}

function getRotation($element) {
    const transform = $element.attr("transform");
    if (transform) {
        const rotateMatch = transform.match(/rotate\(([-\d.]+)\)/);
        if (rotateMatch) {
            return parseFloat(rotateMatch[1]);
        }
    }
    return 0; // Default rotation if no rotate transformation is found
}

function calculateAngle(x1, y1, x2, y2) {
    return Math.atan2(y2 - y1, x2 - x1);
}

function getCueAngle() {
    const poolCue = $("#cue_line");

    const transform = poolCue.attr("transform");
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
    const poolCue = $("#cue_line");

    let cueBallX = parseFloat(cueBall.attr("cx"));
    let cueBallY = parseFloat(cueBall.attr("cy"));


    $("#svg-container svg").on("mousedown", "#cue_line", function (e) {
        let svg = document.querySelector("#svg-container svg");
        let svgPoint = getSVGCoordinates(svg, e);
        let mouseX = svgPoint.x;
        let mouseY = svgPoint.y;

        isDragging = true;
        initialMouseAngle = calculateAngle(cueBallX, cueBallY, mouseX, mouseY);
        initialCueAngle = getCueAngle();
        console.log(initialCueAngle, initialMouseAngle); // Debugging log

    });

    $("#svg-container svg").on("mousemove", function (e) {
        if (isDragging) {
            console.log("Dragging");

            let svg = document.querySelector("#svg-container svg");
            let svgPoint = getSVGCoordinates(svg, e);
            let mouseX = svgPoint.x;
            let mouseY = svgPoint.y;

            console.log("Mouse Move Coordinates:", mouseX, mouseY); // Debugging log

            const dx = mouseX - cueBallX;
            const dy = mouseY - cueBallY;

            const currentMouseAngle = calculateAngle(
                cueBallX,
                cueBallY,
                mouseX,
                mouseY
            );
            // console.log(initialCueAngle, currentMouseAngle, initialMouseAngle); // Debugging log
            const angle =
                initialCueAngle + (currentMouseAngle - initialMouseAngle);
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

    //     let cueLine = $("#cue_line");
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
    //     $("#cue_line").attr({
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
    //         $("#cue_line").attr("visibility", "hidden");
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
