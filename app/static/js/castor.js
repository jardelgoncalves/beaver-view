var btn = document.querySelector("#inserir_queue");
var input = document.querySelector("#todas_queue")

var max = document.querySelector("#max_rate")
var min = document.querySelector("#min_rate")

var exibi = document.querySelector("#minha_tabela")

var vetor = [];
btn.addEventListener('click', function () {
    var x = '';
    var value_max = '';
    var value_min = '';
    if (max.value === '' || isNaN(max.value)) {
        value_max = '-';
        x = '"max_rate":"-",';
    } else {
        value_max = max.value;
        x = '"max_rate":'+max.value + ',';
    }

    if (min.value === '' || isNaN(min.value)) {
        value_min = '-';
        x = '{'+x + '"min_rate":"-"'+'}';
    } else {
        value_min = min.value;
        x = '{'+x + '"min_rate":'+min.value+'}';
    }
    vetor.push(x);
    input.value = '{"queue": ['+vetor+']}';

    exibi.innerHTML = exibi.innerHTML + "<tr><td>" + value_max + "</td><td>" + value_min + "</td></tr>";;
});