var app = angular.module('myApp', []);

app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);

queue()
    .defer(d3.json, "/init_data")
    .await(makeGraphs);

var JsonData;
var period='month';
var kclusters=[];
$(".original_data").click(function () {
    //clusters=null
    $(".buttons").find("button").removeClass("active");
    $(this).addClass("active");
    period = 'month';
    kclusters=[];
    updateGraphs(JsonData);

});

$("#yesbutton").click(function(){
    $(this).addClass("active");
    makePCAGraph(visData);
    makeISOGraph(visData);
    makeMDSGraph(visData);
})


$("#nobutton").click(function(){
    $("#yesbutton").removeClass("active");
    makePCAPlot(visData);
})


$(".random_data").click(function () {
    $(".buttons").find("button").removeClass("active");
    kclusters=[];
    $(this).addClass("active");
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(JsonData),
        dataType: 'json',
        url: '/random_decimation',
        success: function (res) {
            //clusters=null;
            period = 'day'
            updateGraphs(res.result);
            getPCAData(res.result);

        }
    });
});
var clusters;
var clustersN;
$(".adaptive_data").click(function () {
    $(".buttons").find("button").removeClass("active");
    $(this).addClass("active");
    //console.log($("#clusternumber").val());
    //var x=new Object();
    //x["clusters"]=parseInt($("#clusternumber").val());
    //x["data"]=JsonData;
    //console.log(x);
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(JsonData),
        dataType: 'json',
        url: '/adaptive_decimation',
        success: function (res) {
            clusters = new Object()
            clustersN=0
            kclusters=[];
            period = 'day'
            res.result.forEach(function (d, i) {
                kclusters.push(d.length);
                d.forEach(function (d1) {
                    clusters[dateFormat(dateFormat.parse(d1.Date))] = i;
                    // console.log(d1)
                })
                clustersN++;

            })
            data = [];
            for (i = 0; i < res.result.length; i++)
                data = data.concat(res.result[i])
           // console.log(data)
            updateGraphs(data, clusters);
            getPCAData(currentData);
        }
    });
});

var pcaData;
var visData;
function getPCAData(data){
    $("#yesbutton").removeClass("active");
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        dataType: 'json',
        url: '/PCA',
        success: function (res) {
            pcaData=res;

            console.log(kclusters);
            visData=new Object();
            visData["clusters"]=kclusters;
            visData["result"]=pcaData.result;
            makePCAPlot(visData);


            return;

        }
    });
};

function makePCAPlot(data){
  console.log(data);
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data:JSON.stringify(data),
        dataType: 'json',
        url: '/pcaPlot',
        success: function (res) {
            //console.log(res);
            //console.log(res.result);
            $("#Pca-plotchart").empty();
            mpld3.draw_figure("Pca-plotchart", res.result);
            $("#Pca-plotchart>div").css("text-align","center");
            return;

        }
    });
};


function makePCAGraph(data){
  //  console.log(pcaData);
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data:JSON.stringify(data),
        dataType: 'json',
        url: '/pcaGraph',
        success: function (res) {
            //console.log(res);
            $("#Pca-chart").empty();
            mpld3.draw_figure("Pca-chart", res.result);
            $("#Pca-chart>div").css("text-align","center");
            return;

        }
    });
};

function makeISOGraph(data){

    //var x=JSON.parse(JSON.stringify(pcaData));;

    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data:JSON.stringify(data),
        dataType: 'json',
        url: '/isoGraph',
        success: function (res) {
            //console.log(res);
            $("#Iso-chart").empty();
            mpld3.draw_figure("Iso-chart", res.result);
            $("#Iso-chart>div").css("text-align","center");
            return;

        }
    });
};

function makeMDSGraph(data){

    //var x=JSON.parse(JSON.stringify(pcaData));;

    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        data:JSON.stringify(data),
        dataType: 'json',
        url: '/mdsGraph',
        success: function (res) {
            //console.log(res);
            $("#Mds-chart").empty();
            mpld3.draw_figure("Mds-chart", res.result);
            $("#Mds-chart>div").css("text-align","center");
            return;

        }
    });
};


function makeGraphs(error, data) {
    if (error) throw error;
    JsonData = data;
    //$(".pca").disabled =true;
   // console.log(JsonData);
    updateGraphs(data);

};
var currentData;
var dateFormat = d3.time.format("%m/%d/%Y");
function updateGraphs(data, c) {

    if (!c) {
        clusters == null
    }

    data.forEach(function (e) {
        e.dd = dateFormat.parse(e.Date);
    });
    cf = crossfilter(data);
        currentData=data;
  //  console.log(data);
    makeChart(cf, "Volume", data);
    makeChart(cf, "Open", data);
    makeChart(cf, "Close", data);
    makeChart(cf, "Change", data);
    dc.renderAll();

}


function makeChart(cf, X, data) {

    var dim = cf.dimension(function (d) {


        return period == 'month'?d3.time.month(d.dd):d3.time.day(d.dd)

    });
    grp = dim.group().reduceSum(function (d) {
        return d[X];
    });
    ;
    var xExtent = d3.extent(data, function (d) {
        return d.dd;
    });
    chart = dc.barChart("#" + X + "-chart");

    var color=d3.scale.category10().domain(d3.range(0,10));
    chart.width($(".chart-stage").width())
        .height(250)
        .transitionDuration(500)
        .margins({top: 10, right: 50, bottom: 30, left: 100})
        .dimension(dim)
        .group(grp)
        .centerBar(true)
        .x(d3.time.scale().domain(xExtent))
        .elasticY(true)
        .round(period=='month'?d3.time.month.round:d3.time.day.round)
        // define x axis units
        .xUnits(period=='month'?d3.time.months:d3.time.days)
        .colors(color)
        .colorAccessor(function (d) {


            return clusters?clusters[dateFormat(d.x)]:0;


        })

}