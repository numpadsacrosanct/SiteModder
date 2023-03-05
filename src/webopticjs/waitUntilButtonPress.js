var ele = document.createElement('button');
ele.innerText = "BUTTON";
ele.onclick = () => window.buttonSentinel = true;
document.body.prepend(ele);
