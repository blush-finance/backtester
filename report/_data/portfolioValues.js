const report = require("./report.json");

module.exports = function (data) {
  return JSON.stringify(report.portfolioValues);
};
