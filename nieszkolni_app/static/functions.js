function showHide(element) {
  var object = document.getElementById(element);
  if (object.style.display == "none") {
    object.style.display = "block";
  } else {
    object.style.display = "none";
  };
};

function disableButton(button_id) {
  var button = document.getElementById(button_id);
  
  button.onchange = (event) => {
           event.preventDefault();
           button.disabled = true;
         };
  };

function forgetPage(state) {
  if (state == true) {
    history.forward();
    };
  };