# Setup

The backtester will put a `report.json` file into the `_data` directory. Based on this we will create a report by running `npm run build`.

The site is built with 11ty.

The data is injected during compile time. We need to inject the data directly because the browser won't allow access to other files without running a server.

We use Tailwind for the styling and `d3.js` for the graphs