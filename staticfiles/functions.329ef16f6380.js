function showHide(element) {
  var object = document.getElementById(element);
  if (object.style.display == "none") {
    object.style.display = "block";
  } else {
    object.style.display = "none";
  };
}

function disableButton(button_id) {
  var button = document.getElementById(button_id);
  
  button.onchange = (event) => {
           event.preventDefault();
           button.disabled = true;
         };
  }

function forgetPage(state) {
  if (state == true) {
    history.forward();
    };
  }

function showHideWidgets(a, b, c) {
  var a = document.getElementById(a);
  var b = document.getElementById(b);
  var c = document.getElementById(c);

  if (c === undefined) {
    if (a.style.display == "none") {
    a.style.display = "block";
    b.style.display = "none";
    } else {
    a.style.display = "none";
    b.style.display = "none";
    }
  } else {
    if (a.style.display == "none") {
      a.style.display = "block";
      b.style.display = "none";
      c.style.display = "none";
    } else {
      a.style.display = "none";
      b.style.display = "none";
      c.style.display = "none";
    };
  };
}

function stopWatch(command) {
  if (command == true) {
    var beginning = Date(2000, 1, 1, 0, 0);
    var date = new Date().format('m-d-Y h:i:s');
    // var year = date.getFullYear();
    // var month = date.getMonth() + 1;
    // var day = date.getDay();
    alert(date)
  }
}

function monitorClock() {
  var status = document.getElementById('status_info');
  var dot = document.getElementById('clock_info');
  
  if (status.value == 'True') {
    dot.className = 'clock_dot clocked_in';
  } else {
    dot.className = 'clock_dot clocked_out';
  };
}