(async () => {
    let chartData = [];
    let accountsResponse = await fetch('/accounts');
    let accountsResponseJson = await accountsResponse.json();
    let balances = await Promise.all(
          accountsResponseJson.map(async account => {
                let balanceResponse = await fetch(`/balance/cur/${account[0]}`)
                return balanceResponse.json()
          })
    );
    balances.forEach((bal, key) => {
        let name = bal.map(name => name[3]);
        let type = bal.map(type => type[4]);
        let plot = {
            name: name[0],
            x: bal.map(at => at[1]),
            y: bal.map(amt => Number(amt[0].replace(/[^0-9.-]+/g,""))),
            type: 'scatter',
            mode: 'lines+markers'
        }
        // if (type == 'credit') {
        //     plot['line'] = { color: '#ff0000' }
        // }
        chartData.push(plot)
    });
    let layout = {
        title: "here's some stuff",
        autosize: true,
        height: 700
    };
    Plotly.newPlot('chart', chartData, layout);
})();
