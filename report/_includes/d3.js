
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

function createGraph(domNode, data, yLabel) {
  console.log(data)
   // Declare the chart dimensions and margins.
  const width = 928;
  const height = 500;
  const marginTop = 20;
  const marginRight = 30;
  const marginBottom = 30;
  const marginLeft = 40;

  // Declare the x (horizontal position) scale.
  const x = d3
    .scaleUtc()
    .domain(d3.extent(data, d => d.date))
    .range([marginLeft, width - marginRight]);

  // Declare the y (vertical position) scale.
  const y = d3
    .scaleLinear()
    .domain([d3.min(data, d => d.value), d3.max(data, d => d.value)])
    .range([height - marginBottom, marginTop]);

  const groups = Array.from(d3.group(data, d => d.name))
  console.log(groups)

  // Declare the line generator.
  const line = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.value));

  // Create the SVG container.
  const svg = d3.select(domNode)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height])
      .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

  // Add the x-axis.
  svg.append("g")
      .attr("transform", `translate(0,${height - marginBottom})`)
      .call(d3.axisBottom(x).ticks(width / 80).tickSizeOuter(0));

  // Add the y-axis, remove the domain line, add grid lines and a label.
  svg.append("g")
      .attr("transform", `translate(${marginLeft},0)`)
      .call(d3.axisLeft(y).ticks(height / 40))
      .call(g => g.selectAll(".tick line").clone()
          .attr("x2", width - marginLeft - marginRight)
          .attr("stroke-opacity", 0.1))
      .call(g => g.append("text")
          .attr("x", -marginLeft)
          .attr("y", 10)
          .attr("fill", "currentColor")
          .attr("text-anchor", "start")
          .text(yLabel));


  // Append a path for the line.
  svg.selectAll(".line")
      .append("g")
      .attr("class", "line")
      .data(groups)
      .enter()
      .append("path")
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 2)
      .attr('d', (d) => d3.line()
          .x(d => x(d.date))
          .y(d => y(d.value))
          (d[1])
      )

  // Append the SVG element.
  svg.node();
}

// Data will be injected at compile time
let portfolioReturns = {{ portfolioReturns | safe }};
portfolioReturns = portfolioReturns.map(({Date: date, Value: value}) => ({ date: new Date(date), name: 'Portfolio', value}))
createGraph('#portfolioReturnsGraph', portfolioReturns, 'Return (%)')

// Data will be injected at compile time
let portfolioValues = {{ portfolioValues | safe }};
portfolioValues = portfolioValues.map(({Date: date, Value: value}) => ({date: new Date(date), name: 'Portfolio', value}))
createGraph('#portfolioValuesGraph', portfolioValues, 'Value ($)')

// Data will be injected at compile time
let portfolioValueBreakdown = {{ portfolioValueBreakdown | safe }};
portfolioValueBreakdown = portfolioValueBreakdown.map(({Date: date, ...values}) => Object.entries(values).map(([companyName, value]) => ({date: new Date(date), name: companyName, value }))).flat(1)
createGraph('#portfolioValueBreakdownGraph', portfolioValueBreakdown, 'Value ($)')
