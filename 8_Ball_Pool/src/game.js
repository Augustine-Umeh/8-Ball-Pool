$(document).ready(function () {
    var player1Name = localStorage.getItem("player1Name");
    var player2Name = localStorage.getItem("player2Name");
    var gameID = parseInt(localStorage.getItem("gameID"));
    var gameName = localStorage.getItem("gameName");
    var accountID = parseInt(localStorage.getItem("accountID"));

    $("#player1Name").text(player1Name);
    $("#player2Name").text(player2Name);
    $("#playerTurn").text(player1Name);

    $.ajax({
        type: "POST",
        url: "/initializeTable",
        contentType: "application/json",
        data: JSON.stringify({
            accountID: parseInt(accountID),
            gameID: parseInt(gameID)
        }),
        success: function (response) {
            document.getElementById("svg-container").innerHTML = response.svg;

            // Now that the SVG is loaded, select it
            let tableSVG = document.querySelector("#svg-container svg");

            // Make sure svgElement is not null
            if (!tableSVG) {
                console.error("SVG Element not found!");
                return;
            }
            
            createCueAndAimLine();
            setupEventListeners(); 
            shotpowerEventListeners();
        },
        error: function () {
            console.error("Error initializing game");
        },
    });
});

var cue_coord = { x: '999', y: '999' };
function createCueAndAimLine() {
    let cueBall;

    try {
        cueBall = $("#cue_ball");
    
        // Check if the cue ball is not found
        if (cueBall.length === 0) {
            throw new Error("Cue ball not found");
        }
    } catch {
        // If cue ball is not found, create and append it to the SVG container
        let svg = $("#svg-container svg")[0];
   
        // Create a new cue ball element
        cueBall = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        cueBall.setAttribute("id", "cue_ball");
        cueBall.setAttribute("cx", cue_coord.x);
        cueBall.setAttribute("cy", cue_coord.y);
        cueBall.setAttribute("r", "28");
        cueBall.setAttribute("fill", "white");
    
        // Append the cue ball to the SVG container
        svg.appendChild(cueBall);

        cueBall = $("#cue_ball");
    }

    let cueBallX = parseFloat(cueBall.attr("cx"));
    let cueBallY = parseFloat(cueBall.attr("cy"));
    let aimLineY = 0;
    let cueLineY = 0;

    let poolCueLength = 1500;
    let aimLineLength = 2200;

    aimLineY = cueBallY - 56;
    cueLineY = cueBallY + 56;

    // Select the SVG container where you want to append the line
    let svg = $("#svg-container svg")[0];

    let pool_cue = poolcueCreation(
        cueBallX,
        cueBallX,
        cueLineY,
        cueLineY + poolCueLength
    );

    // Create a new SVG aimline element
    let aim_line = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "line"
    );
    aim_line.setAttribute("id", "aim_line");
    aim_line.setAttribute("class", "cue_line");
    aim_line.setAttribute("x1", cueBallX);
    aim_line.setAttribute("y1", aimLineY);
    aim_line.setAttribute("x2", cueBallX); // Set x2 based on desired length from cue ball position
    aim_line.setAttribute("y2", (aimLineY - aimLineLength)); // Keep y2 the same as y1 initially
    aim_line.setAttribute("length", aimLineLength);
    aim_line.setAttribute("stroke", "grey");
    aim_line.setAttribute("stroke-width", "4");
    aim_line.setAttribute("visibility", "visible");

    // Append the line to the SVG container
    svg.appendChild(pool_cue);
    svg.appendChild(aim_line);

    checkLinePath(cueBallX, aimLineY - aimLineLength, cueBallX, cueBallY);
}

function poolcueCreation(x1, x2, y1, y2) {
    let pool_cue = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "line"
    );
    pool_cue.setAttribute("id", "pool_cue");
    pool_cue.setAttribute("class", "cue_line");
    pool_cue.setAttribute("x1", x1);
    pool_cue.setAttribute("y1", y1);
    pool_cue.setAttribute("x2", x2); // Set x2 based on desired length from cue ball position
    pool_cue.setAttribute("y2", y2); // Keep y2 the same as y1 initially
    pool_cue.setAttribute("stroke", "black");
    pool_cue.setAttribute("stroke-width", "25");
    pool_cue.setAttribute("visibility", "visible");

    return pool_cue;
}

function rotatePoolCue(angle) {
    let cueBall = $("#cue_ball");
    let cueBallX = parseFloat(cueBall.attr("cx"));
    let cueBallY = parseFloat(cueBall.attr("cy"));

    let offset = 56;

    // Lengths of the cue line and aim line
    let poolCueLength = 1500;
    let aimLineLength = 2200;

    // Calculate the offset coordinates
    let offsetX = offset * Math.cos(angle);
    let offsetY = offset * Math.sin(angle);

    // Calculate new coordinates for cue line
    let cueLineStartX = cueBallX - offsetX;
    let cueLineStartY = cueBallY - offsetY;
    let cueLineEndX = cueLineStartX - poolCueLength * Math.cos(angle);
    let cueLineEndY = cueLineStartY - poolCueLength * Math.sin(angle);

    // Calculate new coordinates for aim line
    let aimLineStartX = cueBallX + offsetX;
    let aimLineStartY = cueBallY + offsetY;
    let aimLineEndX = aimLineStartX + aimLineLength * Math.cos(angle);
    let aimLineEndY = aimLineStartY + aimLineLength * Math.sin(angle);

    // Update the cue line's position
    $("#pool_cue")
        .attr("x1", cueLineStartX)
        .attr("y1", cueLineStartY)
        .attr("x2", cueLineEndX)
        .attr("y2", cueLineEndY);

    $("#aim_line")
        .attr("x1", aimLineStartX)
        .attr("y1", aimLineStartY)
        .attr("x2", aimLineEndX)
        .attr("y2", aimLineEndY);

    checkLinePath(aimLineEndX, aimLineEndY, cueBallX, cueBallY);
}

function checkLinePath(aimLineEndX, aimLineEndY, cueBallX, cueBallY) {
    const balls = $(".ball");
    const aimLine = $("#aim_line");

    let x1 = parseFloat(aimLine.attr("x1"));
    let y1 = parseFloat(aimLine.attr("y1"));
    let x2 = parseFloat(aimLine.attr("x2"));
    let y2 = parseFloat(aimLine.attr("y2"));

    let closestIntersection = null;
    let closestDistance = Number.POSITIVE_INFINITY;

    balls.each(function () {
        let ball = $(this);
        let ballX = parseFloat(ball.attr("cx"));
        let ballY = parseFloat(ball.attr("cy"));
        let ballRadius = parseFloat(ball.attr("r"));

        if (lineIntersectsCircle(x1, y1, x2, y2, ballX, ballY, ballRadius)) {
            // Calculate intersection point
            let intersectionPoint = calculateIntersectionPoint(
                x1,
                y1,
                x2,
                y2,
                ballX,
                ballY,
                ballRadius
            );

            // Calculate distance from cue ball
            let distance = Math.sqrt(
                (cueBallX - intersectionPoint.x) ** 2 +
                    (cueBallY - intersectionPoint.y) ** 2
            );

            // Update closest intersection if this one is closer
            if (distance < closestDistance) {
                closestIntersection = intersectionPoint;
                closestDistance = distance;
            }
        }
    });

    // If intersection found, adjust aim line to closest intersection point
    if (closestIntersection) {
        aimLine.attr("x2", closestIntersection.x);
        aimLine.attr("y2", closestIntersection.y);
    } else {
        // If no intersection found, reset aim line to normal length
        aimLine.attr("x2", aimLineEndX);
        aimLine.attr("y2", aimLineEndY);
    }
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
    let c = fx * fx + fy * fy - r * r;

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

function calculateIntersectionPoint(x1, y1, x2, y2, cx, cy, r) {
    // Vector from (x1, y1) to (x2, y2)
    let dx = x2 - x1;
    let dy = y2 - y1;

    // Vector from (x1, y1) to the circle center (cx, cy)
    let fx = x1 - cx;
    let fy = y1 - cy;

    let a = dx * dx + dy * dy;
    let b = 2 * (fx * dx + fy * dy);
    let c = fx * fx + fy * fy - r * r;

    let discriminant = b * b - 4 * a * c;

    if (discriminant >= 0) {
        discriminant = Math.sqrt(discriminant);

        // Calculate intersection points
        let t1 = (-b - discriminant) / (2 * a);
        let t2 = (-b + discriminant) / (2 * a);

        // Use the parameter t to find intersection coordinates
        let intersection1 = {
            x: x1 + t1 * dx,
            y: y1 + t1 * dy,
        };

        let intersection2 = {
            x: x1 + t2 * dx,
            y: y1 + t2 * dy,
        };

        // Return the closest intersection point to (x1, y1)
        if (t1 >= 0 && t1 <= 1) {
            return intersection1;
        } else if (t2 >= 0 && t2 <= 1) {
            return intersection2;
        } else {
            // This case should not normally happen if there is an intersection
            return intersection1; // Fallback to intersection1
        }
    }

    // No intersection found (should not normally happen in this context)
    return {
        x: x2,
        y: y2,
    };
}

function calculateAngle(x1, y1, x2, y2) {
    return Math.atan2(y2 - y1, x2 - x1);
}

function getCueAngle() {
    const cue = $("#pool_cue");

    const x1 = parseFloat(cue.attr("x1"));
    const y1 = parseFloat(cue.attr("y1"));
    const x2 = parseFloat(cue.attr("x2"));
    const y2 = parseFloat(cue.attr("y2"));

    const angle = calculateAngle(x1, y1, x2, y2);
    return angle;
}

function getSVGCoordinates(svg, event) {
    var pt = svg.createSVGPoint();
    pt.x = event.clientX;
    pt.y = event.clientY;
    return pt.matrixTransform(svg.getScreenCTM().inverse());
}

function shotpowerEventListeners() {
    var gameID = parseInt(localStorage.getItem("gameID"));
    var accountID = parseInt(localStorage.getItem("accountID"));
    var gameName = String(localStorage.getItem("gameName"));
    var player1Name = String(localStorage.getItem("player1Name"))
    var player2Name = localStorage.getItem("player2Name");

    let isDragging = false;
    let initialY = 0;
    let maxSpeed = 10000;
    let maxDragDistance = 540; // Distance in pixels (from 80 to 620)
    
    let shotLine = document.querySelector("#shot_line");
    let aimLine = document.querySelector("#aim_line");

    let startY1 = parseFloat(shotLine.getAttribute("y1"));
    let startY2 = parseFloat(shotLine.getAttribute("y2"));

    $(".shot-meter-container svg").on("mousedown", "#shot_line", function (e) {
        let svg = document.querySelector(".shot-meter-container svg");
        let svgPoint = getSVGCoordinates(svg, e);

        initialY = svgPoint.y;
        isDragging = true;

        e.preventDefault();
    });

    $(".shot-meter-container svg").on("mousemove", function (e) {
        if (isDragging) {
            let svg = document.querySelector(".shot-meter-container svg");
            let svgPoint = getSVGCoordinates(svg, e);
            let mouseY = svgPoint.y;

            let deltaY = mouseY - initialY;

            let currentY1 = parseFloat(shotLine.getAttribute("y1"));
            let currentY2 = parseFloat(shotLine.getAttribute("y2"));

            let newY1 = currentY1 + deltaY;
            let newY2 = currentY2 + deltaY;

            if (newY1 >= startY1 && newY1 <= startY2) {
                shotLine.setAttribute("y1", newY1);
                shotLine.setAttribute("y2", newY2);

                // Update the initialY for continuous dragging
                initialY = mouseY;
            }
        }
    });

    $(".shot-meter-container svg").on("mouseup", function (e) {
        isDragging = false;

        // Getting Speed
        let currentY1 = parseFloat(shotLine.getAttribute("y1"));
        console.log(`Current Y1: ${currentY1}`);
        let dragDistance = currentY1 - startY1; // Calculate how much the line was dragged back

        // Convert drag distance to speed (mph)
        let speed = (dragDistance / maxDragDistance) * maxSpeed;

        //Getting Direction/Angle
        // Get the direction from the aim_line
        let x1 = parseFloat(aimLine.getAttribute("x1"));
        let y1 = parseFloat(aimLine.getAttribute("y1"));
        let x2 = parseFloat(aimLine.getAttribute("x2"));
        let y2 = parseFloat(aimLine.getAttribute("y2"));

        // Calculate the direction vector
        let dx = x2 - x1;
        let dy = y2 - y1;
        let magnitude = Math.sqrt(dx * dx + dy * dy);

        // Normalize the direction vector
        let directionX = dx / magnitude;
        let directionY = dy / magnitude;

        // Calculate velocity components
        let vx = directionX * speed;
        let vy = directionY * speed;

        console.log(`Shot speed: ${speed.toFixed(2)} ms`);
        console.log(
            `Shot direction: (${directionX.toFixed(2)}, ${directionY.toFixed(
                2
            )})`
        );
        console.log(
            `Velocity vector: (vx: ${vx.toFixed(2)}, vy: ${vy.toFixed(2)})`
        );

        // Send the shot data to the server

        // Prepare the data
        const dataToSend = {
            vectorData: {
                'vx': vx,
                'vy': vy,
            },
        };

        shotTaker = player1Name

        // Send the data using AJAX
        $.ajax({
            type: "POST",
            url: "/processDrag", // This URL should match your server endpoint
            contentType: "application/json",
            data: JSON.stringify({
                "velocity": dataToSend.vectorData,
                "accountID": accountID,
                "gameID": gameID,
                "shotTaker": shotTaker
            }),
            success: function (response) {
                if (response.status === 'Success') {
                    let svgData = response.svgData; // Get the SVG data from the response
                    console.log("svgData: ", Object.keys(svgData).length);
                    let svgArray = Object.values(svgData); // Convert SVG data object to an array
                    
                    cue_coord.x = String(response.cue_coord['x']);
                    cue_coord.y = String(response.cue_coord['y']);
                    // Use promise chaining to ensure order
                    displayNextSVG(svgArray)
                        .then(() => {
                            createCueAndAimLine();
                            setupEventListeners();
                        })
                        .catch((error) => {
                            console.error("Error displaying SVGs:", error);
                        });
                }
                
            },
            error: function (xhr, status, error) {
                console.error("Error sending data:", error);
                console.error("Status:", status);
                console.error("Response Text:", xhr.responseText);
            },
        });

        // Reset the line position
        shotLine.setAttribute("x1", "37.5");
        shotLine.setAttribute("y1", "80");
        shotLine.setAttribute("x2", "37.5");
        shotLine.setAttribute("y2", "620");
    });

    $(".shot-meter-container svg").on("mouseleave", function (e) {
        isDragging = false;
    });
}

function displayNextSVG(svgArray) {

    return new Promise((resolve, reject) => {

        let currentIndex = 0; // Start from the first SVG
        console.log("Received SVG data: ", svgArray);

        function updateSVG() {

            if (currentIndex < svgArray.length) {
                if ($("#svg-container").length) {
                    $("#svg-container").html(svgArray[currentIndex]); // Update the SVG container
                    console.log(`Displaying SVG : ${currentIndex + 1}`);
                } else {
                    console.error("#svg-container not found");
                    reject(new Error("#svg-container not found"));
                    return;
                }
                currentIndex++; // Move to the next SVG
                setTimeout(updateSVG, 10); // Wait for 0.01s before displaying the next SVG
            } else {
                console.log("Finished displaying all SVGs.");
                resolve(); // Resolve the promise when done
            }
        }
        updateSVG(); // Start the SVG update loop
    });
}

function setupEventListeners() {
    let isDragging = false;
    let initialMouseAngle = 0;
    let initialCueAngle = 0;

    $("#svg-container svg").on("mousedown", "#pool_cue", function (e) {
        let svg = document.querySelector("#svg-container svg");
        let svgPoint = getSVGCoordinates(svg, e);
        let mouseX = svgPoint.x;
        let mouseY = svgPoint.y;

        isDragging = true;
        let cueBall = $("#cue_ball");
        initialMouseAngle = calculateAngle(
            parseFloat(cueBall.attr("cx")),
            parseFloat(cueBall.attr("cy")),
            mouseX,
            mouseY
        );

        initialCueAngle = getCueAngle();

        e.preventDefault();
    });

    $("#svg-container svg").on("mousemove", function (e) {
        if (isDragging) {
            let svg = document.querySelector("#svg-container svg");
            let svgPoint = getSVGCoordinates(svg, e);
            let mouseX = svgPoint.x;
            let mouseY = svgPoint.y;

            let cueBall = $("#cue_ball");
            const currentMouseAngle = calculateAngle(
                parseFloat(cueBall.attr("cx")),
                parseFloat(cueBall.attr("cy")),
                mouseX,
                mouseY
            );

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
    //                 createCueAndAimLine();
    //             },
    //             error: function (xhr, status, error) {
    //                 console.error("Error sending data:", error);
    //             },
    //         });
    //     }
    // });

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

/**
 * code for later
 * 
 * function createPoolCueGradient(svg) {
    let gradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
    gradient.setAttribute("id", "poolCueGradient");
    gradient.setAttribute("x1", "0%");
    gradient.setAttribute("y1", "0%");
    gradient.setAttribute("x2", "100%");
    gradient.setAttribute("y2", "0%");

    // Define the gradient colors
    let stop1 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
    stop1.setAttribute("offset", "0%");
    stop1.setAttribute("style", "stop-color:brown;stop-opacity:1");
    gradient.appendChild(stop1);

    let stop2 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
    stop2.setAttribute("offset", "80%");
    stop2.setAttribute("style", "stop-color:lightbrown;stop-opacity:1");
    gradient.appendChild(stop2);

    let stop3 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
    stop3.setAttribute("offset", "100%");
    stop3.setAttribute("style", "stop-color:darkbrown;stop-opacity:1");
    gradient.appendChild(stop3);

    // Append the gradient to the SVG's defs section
    let defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.appendChild(gradient);
    svg.appendChild(defs);
}
 */
