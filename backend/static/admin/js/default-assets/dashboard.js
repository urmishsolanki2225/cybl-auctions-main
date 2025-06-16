$(function () {
    'use strict'
    // AREA CHARTS //
    $('#sparkline3').sparkline('html', {
        width: 320,
        height: 70,
        lineColor: '#450b5a',
        fillColor: 'rgba(69, 11, 90, 0.50)',
    });

    //-------------
    //- BAR CHART -
    //-------------

    // Get context with jQuery - using jQuery's .get() method.
    var barChartCanvas = $('#barChart').get(0).getContext('2d');
    // This will get the first returned node in the jQuery collection.
    var barChart = new Chart(barChartCanvas);

    var barChartData = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
            {
                label: 'Electronics',
                fillColor: '#450b5a',
                strokeColor: '#111111',
                pointColor: '#4ac6ec',
                pointStrokeColor: '#111111',
                pointHighlightFill: '#fff',
                pointHighlightStroke: '#450b5a;',
                data: [5, 4, 3, 7, 5, 10, 3]
			},
            {
                label: 'Digital Goods',
                fillColor: '#462f3f',
                strokeColor: '#111111',
                pointColor: '#111111',
                pointStrokeColor: '#1e88e5',
                pointHighlightFill: '#fff',
                pointHighlightStroke: '#f9784a',
                data: [3, 2, 9, 5, 4, 6, 4]
			}
		  ]
    };


    var barChartOptions = {
        //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
        scaleBeginAtZero: true,
        //Boolean - Whether grid lines are shown across the chart
        scaleShowGridLines: true,
        //String - Colour of the grid lines
        scaleGridLineColor: 'rgba(0,0,0,.05)',
        //Number - Width of the grid lines
        scaleGridLineWidth: 1,
        //Boolean - Whether to show horizontal lines (except X axis)
        scaleShowHorizontalLines: true,
        //Boolean - Whether to show vertical lines (except Y axis)
        scaleShowVerticalLines: true,
        //Boolean - If there is a stroke on each bar
        barShowStroke: true,
        //Number - Pixel width of the bar stroke
        barStrokeWidth: 2,
        //Number - Spacing between each of the X value sets
        barValueSpacing: 30,
        //Number - Spacing between data sets within X values
        barDatasetSpacing: 1,
        //String - A legend template
        legendTemplate: '<ul class="<%=name.toLowerCase()%>-legend"><% for (var i=0; i<datasets.length; i++){%><li><span style="background-color:<%=datasets[i].fillColor%>"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>',
        //Boolean - whether to make the chart responsive
        responsive: true,
        maintainAspectRatio: true
    };

    barChartOptions.datasetFill = false,
        barChart.Bar(barChartData, barChartOptions);


});


(function ($) {
    "use strict";

    function getRandomData() {
        for (data.length > 0 && (data = data.slice(1)); data.length < totalPoints;) {
            var prev = data.length > 0 ? data[data.length - 1] : 50,
                y = prev + 10 * Math.random() - 5;
            0 > y ? y = 0 : y > 90 && (y = 90), data.push(y)
        }
        for (var res = [], i = 0; i < data.length; ++i) res.push([i, data[i]]);
        return res
    }
    for (var data = [], totalPoints = 100, d1 = [], i = 0; 10 >= i; i += 1) d1.push([i, parseInt(30 * Math.random())]);
    for (var d2 = [], i = 0; 20 >= i; i += 1) d2.push([i, parseInt(30 * Math.random())]);
    for (var d3 = [], i = 0; 10 >= i; i += 1) d3.push([i, parseInt(30 * Math.random())]);
    var options = {
        series: {
            shadowSize: 0,
            lines: {
                show: !1,
                lineWidth: 0
            }
        },
        grid: {
            borderWidth: 0,
            labelMargin: 10,
            hoverable: !0,
            clickable: !0,
            mouseActiveRadius: 6
        },
        xaxis: {
            tickDecimals: 0,
            ticks: !1
        },
        yaxis: {
            tickDecimals: 0,
            ticks: !1
        },
        legend: {
            show: !1
        }
    };
    $("#line-chart")[0] && $.plot($("#line-chart"), [{
        data: d1,
        lines: {
            show: !0,
            fill: .98
        },
        label: "Product 1",
        stack: !0,
        color: "#e3e3e3"
		}, {
        data: d3,
        lines: {
            show: !0,
            fill: .98
        },
        label: "Product 2",
        stack: !0,
        color: "#450b5a"
		}], options), $("#recent-items-chart")[0] && $.plot($("#recent-items-chart"), [{
        data: getRandomData(),
        lines: {
            show: !0,
            fill: .99
        },
        label: "Items",
        stack: !0,
        color: "#450b5a"
		}], options), $(".flot-chart")[0] && ($(".flot-chart").bind("plothover", function (event, pos, item) {
        if (item) {
            var x = item.datapoint[0].toFixed(2),
                y = item.datapoint[1].toFixed(2);
            $(".flot-tooltip").html(item.series.label + " of " + x + " = " + y).css({
                top: item.pageY + 5,
                left: item.pageX + 5
            }).show()
        } else $(".flot-tooltip").hide()
    }), $("<div class='flot-tooltip' class='chart-tooltip'></div>").appendTo("body"));

    /*----------------------------
 jQuery curvedLines
------------------------------ */

    for (var d1 = [], i = 0; 10 >= i; i += 1) d1.push([i, parseInt(30 * Math.random())]);
    for (var d2 = [], i = 0; 20 >= i; i += 1) d2.push([i, parseInt(30 * Math.random())]);
    for (var d3 = [], i = 0; 10 >= i; i += 1) d3.push([i, parseInt(30 * Math.random())]);
    var options = {
        series: {
            shadowSize: 0,
            curvedLines: {
                apply: !0,
                active: !0,
                monotonicFit: !0
            },
            lines: {
                show: !1,
                lineWidth: 0,
                fill: 1
            }
        },
        grid: {
            borderWidth: 0,
            labelMargin: 10,
            hoverable: !0,
            clickable: !0,
            mouseActiveRadius: 6
        },
        xaxis: {
            tickDecimals: 0,
            ticks: !1
        },
        yaxis: {
            tickDecimals: 0,
            ticks: !1
        },
        legend: {
            show: !1
        }
    };
    $("#curved-line-chart")[0] && $.plot($("#curved-line-chart"), [{
        data: d1,
        lines: {
            show: !0,
            fill: .98
        },
        label: "Product 1",
        stack: !0,
        color: "#e3e3e3"
    }, {
        data: d3,
        lines: {
            show: !0,
            fill: .98
        },
        label: "Product 2",
        stack: !0,
        color: "#450b5a"
    }], options), $(".flot-chart")[0] && ($(".flot-chart").bind("plothover", function (event, pos, item) {
        if (item) {
            var x = item.datapoint[0].toFixed(2),
                y = item.datapoint[1].toFixed(2);
            $(".flot-tooltip").html(item.series.label + " of " + x + " = " + y).css({
                top: item.pageY + 5,
                left: item.pageX + 5
            }).show()
        } else $(".flot-tooltip").hide()
    }), $("<div class='flot-tooltip' class='chart-tooltip'></div>").appendTo("body"));


    function sparklineBar(id, values, height, barWidth, barColor, barSpacing) {
        $("." + id).sparkline(values, {
            type: "bar",
            height: height,
            barWidth: barWidth,
            barColor: barColor,
            barSpacing: barSpacing
        })
    }

    function sparklineLine(id, values, width, height, lineColor, fillColor, lineWidth, maxSpotColor, minSpotColor, spotColor, spotRadius, hSpotColor, hLineColor) {
        $("." + id).sparkline(values, {
            type: "line",
            width: width,
            height: height,
            lineColor: lineColor,
            fillColor: fillColor,
            lineWidth: lineWidth,
            maxSpotColor: maxSpotColor,
            minSpotColor: minSpotColor,
            spotColor: spotColor,
            spotRadius: spotRadius,
            highlightSpotColor: hSpotColor,
            highlightLineColor: hLineColor
        })
    }

    function sparklinePie(id, values, width, height, sliceColors) {
        $("." + id).sparkline(values, {
            type: "pie",
            width: width,
            height: height,
            sliceColors: sliceColors,
            offset: 0,
            borderWidth: 0
        })
    }

    function easyPieChart(id, trackColor, scaleColor, barColor, lineWidth, lineCap, size) {
        $("." + id).easyPieChart({
            trackColor: trackColor,
            scaleColor: scaleColor,
            barColor: barColor,
            lineWidth: lineWidth,
            lineCap: lineCap,
            size: size
        })
    }
    $(".stats-bar")[0] && sparklineBar("stats-bar", [6, 4, 8, 6, 5, 6, 7, 8, 3, 5, 9, 5, 8, 4], "35px", 3, "#450b5a", 2), $(".stats-bar-2")[0] && sparklineBar("stats-bar-2", [4, 7, 6, 2, 5, 3, 8, 6, 6, 4, 8, 6, 5, 8], "35px", 3, "#01c0c8", 2), $(".stats-line")[0] && sparklineLine("stats-line", [9, 4, 6, 5, 6, 4, 5, 7, 9, 3, 6, 5], 68, 35, "#fb9678", "#fb9678", 1.25, "#fb9678", "#fb9678", "#fb9678", 3, "#fb9678", "#fb9678"), $(".stats-line-2")[0] && sparklineLine("stats-line-2", [5, 6, 3, 9, 7, 5, 4, 6, 5, 6, 4, 9], 68, 35, "#450b5a", "#450b5a", 1.25, "#450b5a", "#450b5a", "#450b5a", 3, "#450b5a", "#450b5a"), $(".stats-pie")[0] && sparklinePie("stats-pie", [20, 35, 30, 5], 45, 45, ["#fff", "rgba(255,255,255,0.7)", "rgba(255,255,255,0.4)", "rgba(255,255,255,0.2)"]), $(".dash-widget-visits")[0] && sparklineLine("dash-widget-visits", [9, 4, 6, 5, 6, 4, 5, 7, 9, 3, 6, 5], "100%", "70px", "#450b5a", "#450b5a", 2, "#450b5a", "#450b5a", "#450b5a", 5, "#450b5a", "#450b5a"), $(".main-pie")[0] && easyPieChart("main-pie", "rgba(255,255,255,0.2)", "rgba(255,255,255,0)", "rgba(255,255,255,0.7)", 2, "butt", 148), $(".sub-pie-1")[0] && easyPieChart("sub-pie-1", "rgba(255,255,255,0.2)", "rgba(255,255,255,0)", "rgba(255,255,255,0.7)", 2, "butt", 90), $(".sub-pie-2")[0] && easyPieChart("sub-pie-2", "rgba(255,255,255,0.2)", "rgba(255,255,255,0)", "rgba(255,255,255,0.7)", 2, "butt", 90)

    /*--------------------------
     Bar chart Active Class
    ---------------------------- */
    var data1 = [
            [1, 60],
            [2, 30],
            [3, 50],
            [4, 100],
            [5, 10],
            [6, 90],
            [7, 85]
        ],
        data2 = [
            [1, 20],
            [2, 90],
            [3, 60],
            [4, 40],
            [5, 100],
            [6, 25],
            [7, 65]
        ],
        data3 = [
            [1, 100],
            [2, 20],
            [3, 60],
            [4, 90],
            [5, 80],
            [6, 10],
            [7, 5]
        ],
        barData = [{
            label: "Product",
            data: data1,
            color: "#450b5a"
        }, {
            label: "Product",
            data: data2,
            color: "#fb9678"
        }, {
            label: "Product",
            data: data3,
            color: "#01c0c8"
        }];
    $("#bar-chart")[0] && $.plot($("#bar-chart"), barData, {
        series: {
            bars: {
                show: !0,
                barWidth: .05,
                order: 1,
                fill: 1
            }
        },
        grid: {
            borderWidth: 1,
            borderColor: "#eee",
            show: !0,
            hoverable: !0,
            clickable: !0
        },
        yaxis: {
            tickColor: "#eee",
            tickDecimals: 0,
            font: {
                lineHeight: 14,
                style: "normal",
                color: "#450b5a"
            },
            shadowSize: 0
        },
        xaxis: {
            tickColor: "#fff",
            tickDecimals: 0,
            font: {
                lineHeight: 14,
                style: "normal",
                color: "#450b5a"
            },
            shadowSize: 0
        },
        legend: {
            container: ".flc-bar",
            backgroundOpacity: .5,
            noColumns: 0,
            backgroundColor: "white",
            lineWidth: 0
        }
    }), $(".flot-chart")[0] && ($(".flot-chart").bind("plothover", function (event, pos, item) {
        if (item) {
            var x = item.datapoint[0].toFixed(2),
                y = item.datapoint[1].toFixed(2);
            $(".flot-tooltip").html(item.series.label + " of " + x + " = " + y).css({
                top: item.pageY + 5,
                left: item.pageX + 5
            }).show()
        } else $(".flot-tooltip").hide()
    }), $("<div class='flot-tooltip' class='chart-tooltip'></div>").appendTo("body"))


    /*--------------------------
     Dynamic chart Active Class
    ---------------------------- */

    function getRandomData() {
        for (data.length > 0 && (data = data.slice(1)); data.length < totalPoints;) {
            var prev = data.length > 0 ? data[data.length - 1] : 50,
                y = prev + 10 * Math.random() - 5;
            0 > y ? y = 0 : y > 90 && (y = 90), data.push(y)
        }
        for (var res = [], i = 0; i < data.length; ++i) res.push([i, data[i]]);
        return res
    }

    function update() {
        plot.setData([getRandomData()]), plot.draw(), setTimeout(update, updateInterval)
    }
    var data = [],
        totalPoints = 300,
        updateInterval = 30;
    if ($("#dynamic-chart")[0]) {
        var plot = $.plot("#dynamic-chart", [getRandomData()], {
            series: {
                label: "Product",
                lines: {
                    show: !0,
                    lineWidth: .2,
                    fill: .99
                },
                color: "#450b5a",
                shadowSize: 0
            },
            yaxis: {
                min: 0,
                max: 100,
                tickColor: "#eee",
                font: {
                    lineHeight: 14,
                    style: "normal",
                    color: "#450b5a"
                },
                shadowSize: 0
            },
            xaxis: {
                tickColor: "#eee",
                show: !0,
                font: {
                    lineHeight: 14,
                    style: "normal",
                    color: "#450b5a"
                },
                shadowSize: 0,
                min: 0,
                max: 250
            },
            grid: {
                borderWidth: 1,
                borderColor: "#eee",
                labelMargin: 10,
                hoverable: !0,
                clickable: !0,
                mouseActiveRadius: 6
            },
            legend: {
                show: !1
            }
        });
        update()
    }

})(jQuery);