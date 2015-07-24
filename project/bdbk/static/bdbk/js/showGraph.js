var svg = d3.select("#svg-container").append("svg")
      .attr("width", "60%");

var width = svg.style("width").replace("px", "")*1.0;
var height = width*0.618;

svg.attr("height", height);

var force = d3.layout.force()
      .gravity(.05)
      .distance(100)
      .charge(-100)
      .size([width, height]);
var force_started = false;

var color = d3.scale.category20();

$(window).resize(function(){
  width = svg.style("width").replace("px", "")*1.0;
  height = width*0.618;
  svg.attr("height", height);
  force.size([width, height]);
  if(force_started)
    force.start();
});

d3.json(data_url, function(error, json){
  if(error) throw error;

  // fix the first node
  json.nodes[0].x = width / 2;
  json.nodes[0].y = height / 2;
  json.nodes[0].fixed = true;

  force.nodes(json.nodes)
    .links(json.links)
    .linkDistance(70)
    .start();

  var link = svg.selectAll(".link")
        .data(json.links)
        .enter().append("line")
        .attr("class", "link");

  var node = svg.selectAll(".node")
        .data(json.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);

  node.append("circle")
    .attr("class", "circle")
    .style("fill", function(d){return color(d.group);})
    .attr("r", 5)
    .attr("x", -8)
    .attr("y", -8)
    .attr("width", 16)
    .attr("height", 16);

  node.append("a")
    .append("text")
    .attr("dx", 7)
    .attr("dy", ".35em")
    .text(function(d) { return d.name; });

  svg.style("opacity", 1e-6)
    .transition()
    .duration(1000)
    .style("opacity", 1);

  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
  });
  force_started = true;

});
