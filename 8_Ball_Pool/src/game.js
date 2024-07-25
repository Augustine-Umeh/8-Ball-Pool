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
var isOntable = true;
var ballNumbers = [];
var play1balls = [1, 11, 2, 10, 8, 3, 9, 14, 4, 13, 12, 5, 15, 6, 7];
var play2balls = [1, 11, 2, 10, 8, 3, 9, 14, 4, 13, 12, 5, 15, 6, 7];
var sameTables = false;
var winner = null;
function createCueAndAimLine() {

    if (isOntable) {
        let cueBall = $("#cue_ball");

        if (sameTables) {
            moveCueBall(document.getElementById("cue_ball"));
            isOntable = false;
            return;
        }

        let cueBallX = parseFloat(cueBall.attr("cx"));
        let cueBallY = parseFloat(cueBall.attr("cy"));

        let aimLineX = cueBallX - 48;
        let cueLineX = cueBallX + 48;

        let poolCueLength = 1500;
        let aimLineLength = 7000;

        let svg = $("#svg-container svg")[0];

        let pool_cue = document.createElementNS("http://www.w3.org/2000/svg", "line");
        pool_cue.setAttribute("id", "pool_cue");
        pool_cue.setAttribute("class", "cue_line");
        pool_cue.setAttribute("x1", cueLineX);
        pool_cue.setAttribute("y1", cueBallY);
        pool_cue.setAttribute("x2", cueLineX + poolCueLength);
        pool_cue.setAttribute("y2", cueBallY);
        pool_cue.setAttribute("stroke", "black");
        pool_cue.setAttribute("stroke-width", "25");
        pool_cue.setAttribute("visibility", "visible");

        let aim_line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        aim_line.setAttribute("id", "aim_line");
        aim_line.setAttribute("class", "cue_line");
        aim_line.setAttribute("x1", aimLineX);
        aim_line.setAttribute("y1", cueBallY);
        aim_line.setAttribute("x2", aimLineX - aimLineLength);
        aim_line.setAttribute("y2", cueBallY);
        aim_line.setAttribute("length", aimLineLength);
        aim_line.setAttribute("stroke", "grey");
        aim_line.setAttribute("stroke-width", "4");
        aim_line.setAttribute("visibility", "visible");

        svg.appendChild(pool_cue);
        svg.appendChild(aim_line);

        checkLinePath(aimLineX - aimLineLength, cueBallY, cueBallX, cueBallY);
    } else {
        let svg = $("#svg-container svg")[0];
        let cueBall = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        cueBall.setAttribute("id", "cue_ball");
        cueBall.setAttribute("cx", cue_coord.x);
        cueBall.setAttribute("cy", cue_coord.y);
        cueBall.setAttribute("r", "28");
        cueBall.setAttribute("fill", "white");

        svg.appendChild(cueBall);
        moveCueBall(document.getElementById("cue_ball"));

        isOntable = false;
    }

    ballNumbers = getBallNumbersFromSVG();
    console.log(ballNumbers);
}

function moveCueBall(cueBall) {
    let svg = document.querySelector("#svg-container svg");
    let isDragging = false;

    let cueBallX = parseFloat(cueBall.getAttribute("cx"));
    let cueBallY = parseFloat(cueBall.getAttribute("cy"));

    let aimLineX = cueBallX - 48;
    let cueLineX = cueBallX + 48;

    let poolCueLength = 1500;
    let aimLineLength = 7000;

    let pool_cue = document.createElementNS("http://www.w3.org/2000/svg", "line");
    pool_cue.setAttribute("id", "pool_cue");
    pool_cue.setAttribute("class", "cue_line");
    pool_cue.setAttribute("x1", cueLineX);
    pool_cue.setAttribute("y1", cueBallY);
    pool_cue.setAttribute("x2", cueLineX + poolCueLength);
    pool_cue.setAttribute("y2", cueBallY);
    pool_cue.setAttribute("stroke", "black");
    pool_cue.setAttribute("stroke-width", "25");
    pool_cue.setAttribute("visibility", "visible");

    let aim_line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    aim_line.setAttribute("id", "aim_line");
    aim_line.setAttribute("class", "cue_line");
    aim_line.setAttribute("x1", aimLineX);
    aim_line.setAttribute("y1", cueBallY);
    aim_line.setAttribute("x2", aimLineX - aimLineLength);
    aim_line.setAttribute("y2", cueBallY);
    aim_line.setAttribute("length", aimLineLength);
    aim_line.setAttribute("stroke", "grey");
    aim_line.setAttribute("stroke-width", "4");
    aim_line.setAttribute("visibility", "visible");

    svg.appendChild(pool_cue);
    svg.appendChild(aim_line);

    checkLinePath(aimLineX - aimLineLength, cueBallY, cueBallX, cueBallY);

    cueBall.addEventListener('mousedown', (e) => {
        let pool_cue = $("#pool_cue");
        let aim_line = $("#aim_line");

        isDragging = true;
        e.preventDefault();

        pool_cue.hide();
        aim_line.hide();
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            let coords = getSVGCoordinates(svg, e);
            let x = coords.x;
            let y = coords.y;
            let radius = parseFloat(cueBall.getAttribute('r'));

            if (isValidPosition(x, y, radius)) {
                cue_coord.x = x;
                cue_coord.y = y;
                cueBall.setAttribute('cx', cue_coord.x);
                cueBall.setAttribute('cy', cue_coord.y);
            }
        }
    });

    cueBall.addEventListener('mouseup', () => {
        cue_coord.x = cueBall.getAttribute("cx");
        cue_coord.y = cueBall.getAttribute("cy");
        isDragging = false;

        showPoolCue(poolCueLength, aimLineLength);
    });
}

function showPoolCue(poolCueLength, aimLineLength) {
    let cueBall = $("#cue_ball");
    let cueBallX = parseFloat(cueBall.attr("cx"));
    let cueBallY = parseFloat(cueBall.attr("cy"));

    let aimLineX = cueBallX - 48;
    let cueLineX = cueBallX + 48;

    let pool_cue = $("#pool_cue");
    pool_cue.attr("x1", cueLineX);
    pool_cue.attr("y1", cueBallY);
    pool_cue.attr("x2", cueLineX + poolCueLength);
    pool_cue.attr("y2", cueBallY);

    let aim_line = $("#aim_line");
    aim_line.attr("x1", aimLineX);
    aim_line.attr("y1", cueBallY);
    aim_line.attr("x2", aimLineX - aimLineLength);
    aim_line.attr("y2", cueBallY);

    pool_cue.show();
    aim_line.show();

    checkLinePath(aimLineX - aimLineLength, cueBallY, cueBallX, cueBallY);
}

function isValidPosition(x, y, radius) {
    let tableWidth = 2700;
    let tableHeight = 1350;
    let pocketRadius = 112;

    if (x - radius < 0 || x + radius > tableWidth || y - radius < 0 || y + radius > tableHeight) {
        return false;
    }

    let pockets = [
        { cx: 0, cy: 0 },
        { cx: tableWidth / 2, cy: 0 },
        { cx: tableWidth, cy: 0 },
        { cx: 0, cy: tableHeight },
        { cx: tableWidth / 2, cy: tableHeight },
        { cx: tableWidth, cy: tableHeight }
    ];

    for (let pocket of pockets) {
        let distance = Math.sqrt(Math.pow(x - pocket.cx, 2) + Math.pow(y - pocket.cy, 2));
        if (distance < pocketRadius + radius) {
            return false;
        }
    }

    const balls = $("g.ball circle, circle.ball");

    for (let ball of balls) {
        let ballX = parseFloat(ball.getAttribute('cx'));
        let ballY = parseFloat(ball.getAttribute('cy'));
        let ballRadius = parseFloat(ball.getAttribute('r'));
        let distance = Math.sqrt(Math.pow(x - ballX, 2) + Math.pow(y - ballY, 2));
        if (distance < radius + ballRadius) {
            return false;
        }
    }
    return true;
}

function rotatePoolCue(angle) {
    let cueBall = $("#cue_ball");
    let cueBallX = parseFloat(cueBall.attr("cx"));
    let cueBallY = parseFloat(cueBall.attr("cy"));

    let offset = 56;

    // Lengths of the cue line and aim line
    let poolCueLength = 1500;
    let aimLineLength = 7000;

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
    const balls = $("g.ball circle, circle.ball");
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

function getBallNumbersFromSVG() {
    // Retrieve the SVG element
    let svg = document.getElementById("table");

    if (!svg) {
        console.error("SVG not found!");
        return [];
    }

    // Get all text elements inside the SVG
    let textElements = svg.getElementsByTagName("text");
    var ballNumbers = [];

    // Iterate through text elements and extract ball numbers
    for (let i = 0; i < textElements.length; i++) {
        const textElement = textElements[i];
        const ballNumber = textElement.textContent.trim();

        // Check if the text content is a number
        if (!isNaN(ballNumber)) {
            ballNumbers.push(ballNumber);
        }
    }

    return ballNumbers;
}

function shotpowerEventListeners() {
    var gameID = parseInt(localStorage.getItem("gameID"));
    var accountID = parseInt(localStorage.getItem("accountID"));
    var player1Name = String(localStorage.getItem("player1Name"));
    var player2Name = String(localStorage.getItem("player2Name"));
    var shotTaker = Math.random() < 0.5 ? player1Name : player2Name;

    let isDragging = false;
    let initialY = 0;
    let maxSpeed = 6000;
    let maxDragDistance = 540; // Distance in pixels (from 80 to 620)

    let shotLine = document.querySelector("#shot_line");

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

        let aimLine = document.querySelector("#aim_line");

        // Getting Speed
        let currentY1 = parseFloat(shotLine.getAttribute("y1"));
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

        if (vx < 3 && vx > -3) {
            if (vy < 0.0) {
                vx = -7.1383338342;
            } else {
                vx = 9.2484224842;
            }
        } else if (vy < 3 && vy > -3) {
            if (vx < 0.0) {
                vy = -7.32746462;
            } else {
                vy = 9.737474743;
            }
        }

        console.log(`Shot speed: ${speed.toFixed(2)} ms`);

        // Send the shot data to the server
        // Prepare the data
        const dataToSend = {
            vectorData: {
                'vx': vx,
                'vy': vy,
            },
        };

        console.log("Current Player: ", shotTaker);
        // Send the data using AJAX
        $.ajax({
            type: "POST",
            url: "/processDrag",
            contentType: "application/json",
            data: JSON.stringify({
                "velocity": dataToSend.vectorData,
                "accountID": accountID,
                "gameID": gameID,
                "shotTaker": shotTaker,
                "cueBallPos": cue_coord,
                "isOntable": isOntable,
                "ballNumbers": ballNumbers,
                "play1balls": play1balls,
                "play2balls": play2balls
            }),
            success: function (response) {
                if (response.status === 'Success') {
                    let svgData = response.svgData; // Get the SVG data from the response
                    console.log("svgData: ", Object.keys(svgData).length);
                    let svgArray = Object.values(svgData); // Convert SVG data object to an array

                    isOntable = response.isOntable
                    cue_coord.x = String(response.cueBallPos[0]);
                    cue_coord.y = String(response.cueBallPos[1]);
                    shotTaker = response.shotTaker

                    play1balls = response.play1balls;
                    play2balls = response.play2balls;

                    console.log(`${player1Name}'s balls: [${response.play1balls}]`);
                    console.log(`${player2Name}'s balls: [${response.play2balls}]`);

                    sameTables = response.sameTables;

                    endResult = response.endResult


                    // Use promise chaining to ensure order
                    displayNextSVG(svgArray)
                        .then(() => {
                            setTimeout(() => {
                                createCueAndAimLine();
                                setupEventListeners();
                            }, 300);
                        })
                        .catch((error) => {
                            console.error("Error displaying SVGs:", error);
                        });

                    console.log("Updates: ",);
                    if (sameTables) {
                        console.log("Scratch!!");
                    }
                    for (let i = 0; i < endResult.length; i++) {
                        console.log(endResult[i]);
                    }

                    winner = response.winner
                    if (winner) {
                        const svgContainer = $(".shot-meter-container svg");
                        svgContainer.hide()
                        console.log(`${winner} is the winner`);
                        console.log("Game over");
                        return;
                    }
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

        function updateSVG() {
            if (currentIndex < svgArray.length) {
                if ($("#svg-container").length) {
                    $("#svg-container").html(svgArray[currentIndex]); // Update the SVG container
                } else {
                    console.error("#svg-container not found");
                    reject(new Error("#svg-container not found"));
                    return;
                }
                currentIndex++; // Move to the next SVG
                setTimeout(updateSVG, 11); // Wait for 0.01s before displaying the next SVG
            } else {
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
}

// function createPoolCueGradient(svg) {
//     let gradient = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
//     gradient.setAttribute("id", "poolCueGradient");
//     gradient.setAttribute("x1", "0%");
//     gradient.setAttribute("y1", "0%");
//     gradient.setAttribute("x2", "100%");
//     gradient.setAttribute("y2", "0%");

//     // Define the gradient colors
//     let stop1 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
//     stop1.setAttribute("offset", "0%");
//     stop1.setAttribute("style", "stop-color:brown;stop-opacity:1");
//     gradient.appendChild(stop1);

//     let stop2 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
//     stop2.setAttribute("offset", "80%");
//     stop2.setAttribute("style", "stop-color:lightbrown;stop-opacity:1");
//     gradient.appendChild(stop2);

//     let stop3 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
//     stop3.setAttribute("offset", "100%");
//     stop3.setAttribute("style", "stop-color:darkbrown;stop-opacity:1");
//     gradient.appendChild(stop3);

//     // Append the gradient to the SVG's defs section
//     let defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
//     defs.appendChild(gradient);
//     svg.appendChild(defs);
// }
