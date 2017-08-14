/**
 * 두 개체를 연결하는 그림을 생성함
 * @param canvas 그림을 그릴 캔바스 개체
 * @param offset 각 개체 위치 인식을 위한 오프셋
 * @param a 첫번째 개체
 * @param b 두번째 개체
 * @param h 높이
 */
function linkTwo(canvas, offset, a, b, h) {
    drawCurvedArrow(canvas, getCurvedPoints({
        sx: a.offset().left + a.width() / 2 - offset,
        ex: b.offset().left + b.width() / 2 - offset,
        sy: h - 5
    }));
}

/**
 * 캔바스에 Quadratic 커브와 화살표를 그림
 * @param canvas 그림을 그릴 캔바스 개체
 * @param pts 그림을 그리기 위한 좌표들
 */
function drawCurvedArrow(canvas, pts) {
    const ctx = canvas.getContext("2d");
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#f39800";
    ctx.fillStyle = "#f39800";
    const arrowSize = ctx.lineWidth + 0.25;
    const endingAngle = getEndingAngle(pts);

    // draw the arrow shaft
    ctx.moveTo(pts.sx, pts.sy);
    ctx.quadraticCurveTo(pts.cx1, pts.cy1, pts.m1x, pts.m1y);
    ctx.lineTo(pts.m2x, pts.m2y);
    ctx.quadraticCurveTo(pts.cx2, pts.cy2, pts.ex, pts.ey);
    ctx.stroke();

    // draw the arrow head
    ctx.beginPath();
    ctx.save();
    ctx.translate(pts.ex, pts.ey);
    ctx.rotate(endingAngle);
    ctx.moveTo(0, 0);
    ctx.lineTo(0, -arrowSize * 1.5);
    ctx.lineTo(arrowSize * 3, 0);
    ctx.lineTo(0, arrowSize * 1.5);
    ctx.lineTo(0, 0);
    ctx.closePath();
    ctx.stroke();
    ctx.fill();
    ctx.restore();
}

/**
 * 그림을 그리기 위한 완전한 좌표들을 구함
 * @param pts
 * @returns {*}
 */
function getCurvedPoints(pts) {
    const h = Math.pow(pts.ex - pts.sx, 0.75);
    pts.sx = pts.sx - 5; // 커브의 시작점 약간 이동
    pts.ex = pts.ex - 12; // 커브의 끝점 약간 이동
    pts.ey = pts.sy - 6;
    pts.m1x = pts.sx + h;
    pts.m1y = pts.sy - h;
    pts.m2x = pts.ex - h;
    pts.m2y = pts.sy - h;
    pts.cx1 = pts.sx;
    pts.cy1 = pts.sy - h;
    pts.cx2 = pts.ex - h * 0.25;
    pts.cy2 = pts.sy - h;
    return pts
}

/**
 * 끝나는 화살표를 그리기 위한 회전 각도를 구함
 * @param pts
 * @returns {number}
 */
function getEndingAngle(pts) {
    var pointNearEnd = getCubicBezierXYatT({
        x: pts.sx,
        y: pts.sy
    }, {
        x: pts.cx1,
        y: pts.cy1
    }, {
        x: pts.cx2,
        y: pts.cy2
    }, {
        x: pts.ex,
        y: pts.ey
    }, 0.99);
    var dx = pts.ex - pointNearEnd.x;
    var dy = pts.ey - pointNearEnd.y;
    return Math.atan2(dy, dx);
}

/**
 * 회전 각도를 구하기 위한 하위 함수 (1)
 * @param startPt
 * @param controlPt1
 * @param controlPt2
 * @param endPt
 * @param T
 * @returns {{x, y}}
 */
function getCubicBezierXYatT(startPt, controlPt1, controlPt2, endPt, T) {
    var x = getCubicN(T, startPt.x, controlPt1.x, controlPt2.x, endPt.x);
    var y = getCubicN(T, startPt.y, controlPt1.y, controlPt2.y, endPt.y);
    return {x: x, y: y};
}

/**
 * 회전 각도를 구하기 위한 하위 함수 (2)
 * @param T
 * @param a
 * @param b
 * @param c
 * @param d
 * @returns {*}
 */
function getCubicN(T, a, b, c, d) {
    var t2 = T * T;
    var t3 = t2 * T;
    return a + (-a * 3 + T * (3 * a - a * T)) * T + (3 * b + T * (-6 * b + b * 3 * T)) * T + (c * 3 - c * 3 * T) * t2 + d * t3;
}
