import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

// A helper to shorten day names (or any x-labels you want to abbreviate).
const DAY_ABBREV = {
  Monday: "Mon",
  Tuesday: "Tue",
  Wednesday: "Wed",
  Thursday: "Thu",
  Friday: "Fri",
  Saturday: "Sat",
  Sunday: "Sun",
};

/**
 * A D3-based Heatmap that displays data for a single season.
 *
 * Props:
 * - dataObject: {
 *     "Winter": [ { x: "Monday", y: "11-1", value: 8 }, ... ],
 *     "Spring": [ { x, y, value }, ... ],
 *     "Summer": [ ... ],
 *     "Fall":   [ ... ]
 *   }
 * - season: "Winter" | "Spring" | "Summer" | "Fall"
 * - width: number (optional, default 450)
 * - height: number (optional, default 450)
 */
function D3Heatmap({ dataObject, season, width = 450, height = 450 }) {
  const svgRef = useRef(null);

  // Extract data for this season. Rename { x, y } to { group, variable }.
  const rawSeasonData = dataObject?.[season] || [];
  const data = rawSeasonData.map((item) => ({
    group: item.x,
    variable: item.y,
    value: item.value,
  }));

  useEffect(() => {
    // 1. Early exit if there's no data
    if (!data || data.length === 0) return;

    // 2. Define margins and compute inner width/height
    const margin = { top: 80, right: 25, bottom: 60, left: 50 };
    const w = width - margin.left - margin.right;
    const h = height - margin.top - margin.bottom;

    // Clear previous render (if any)
    d3.select(svgRef.current).selectAll("*").remove();

    // 3. Create the SVG group
    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // 4. Collect unique labels for x-axis (group) & y-axis (variable)
    const xLabels = [...new Set(data.map((d) => d.group))];
    const yLabels = [...new Set(data.map((d) => d.variable))];

    // 5. Create band scales
    const x = d3.scaleBand().range([0, w]).domain(xLabels).padding(0.05);
    const y = d3.scaleBand().range([h, 0]).domain(yLabels).padding(0.05);

    // 6. Add x-axis with shortened labels
    const xAxis = d3.axisBottom(x).tickSize(0).tickFormat((d) => DAY_ABBREV[d] || d);
    svg
      .append("g")
      .attr("transform", `translate(0, ${h})`)
      .call(xAxis)
      .style("font-size", "14px") // adjust to your preference
      .select(".domain")
      .remove();

    // 7. Add y-axis
    svg
      .append("g")
      .call(d3.axisLeft(y).tickSize(0))
      .style("font-size", "14px")
      .select(".domain")
      .remove();

    // 8. Determine color domain from data
    const values = data.map((d) => d.value);
    let minVal = Math.min(...values);
    let maxVal = Math.max(...values);
    if (minVal === maxVal) {
      // If all values are the same, create a small range so the scale won't collapse
      maxVal = minVal + 1;
    }

    // 9. Use a "heat-like" color scale (yellow → red)
    const colorScale = d3.scaleSequential(d3.interpolateYlOrRd).domain([minVal, maxVal]);

    // 10. Tooltip
    const tooltip = d3
      .select("body")
      .append("div")
      .style("position", "absolute")
      .style("opacity", 0)
      .attr("class", "tooltip")
      .style("background-color", "white")
      .style("border", "solid 1px #999")
      .style("border-radius", "5px")
      .style("padding", "5px")
      .style("font-size", "14px");

    const handleMouseOver = function () {
      tooltip.style("opacity", 1);
      d3.select(this).style("stroke", "black").style("opacity", 1);
    };

    const handleMouseMove = function (event, d) {
      tooltip
        .html(`Value: <strong>${d.value}</strong>`)
        .style("left", event.pageX + 15 + "px")
        .style("top", event.pageY - 10 + "px");
    };

    const handleMouseLeave = function () {
      tooltip.style("opacity", 0);
      d3.select(this).style("stroke", "none").style("opacity", 0.8);
    };

    // 11. Draw rectangles
    svg
      .selectAll("rect")
      .data(data, (d) => `${d.group}:${d.variable}`)
      .join("rect")
      .attr("x", (d) => x(d.group))
      .attr("y", (d) => y(d.variable))
      .attr("width", x.bandwidth())
      .attr("height", y.bandwidth())
      .attr("rx", 4)
      .attr("ry", 4)
      .style("fill", (d) => colorScale(d.value))
      .style("stroke-width", 2)
      .style("stroke", "none")
      .style("opacity", 0.8)
      .on("mouseover", handleMouseOver)
      .on("mousemove", handleMouseMove)
      .on("mouseleave", handleMouseLeave);

    // 12. Title
    svg
      .append("text")
      .attr("x", 0)
      .attr("y", -40)
      .style("font-size", "20px")
      .style("font-weight", "bold")
      .text(`${season}`);

    // 13. Cleanup: remove tooltip on unmount
    return () => {
      tooltip.remove();
    };
  }, [data, width, height, season]);

  return <svg ref={svgRef} />;
}

export default D3Heatmap;