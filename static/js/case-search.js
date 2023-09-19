/* Bookmarklet Case-Sensitive Search */

function search() {

    /* Prompt the user for search terms */
    var text = prompt("Search for:", "");
    if (text == null || text.length == 0) return;

    /* If there any previously highlighed words,
    remove them by setting the background to transparent */

    var spans = document.getElementsByClassName("labnol");

    if (spans) {
        for (var i = 0; i < spans.length; i++) {
            spans[i].style.backgroundColor = "transparent";
        }
    }

    /* Search Code is courtesy Jesse Ruderman */
    function searchWithinNode(node, te, len) {
        var pos, skip, spannode, middlebit, endbit, middleclone;
        skip = 0;
        if (node.nodeType == 3) {
            pos = node.data.indexOf(te);
            if (pos >= 0) {
                spannode = document.createElement("span");
                spannode.setAttribute("class", "labnol");
                spannode.style.backgroundColor = "yellow";
                middlebit = node.splitText(pos);
                endbit = middlebit.splitText(len);
                middleclone = middlebit.cloneNode(true);
                spannode.appendChild(middleclone);
                middlebit.parentNode.replaceChild(spannode, middlebit);
                skip = 1;
            }
        } else if (node.nodeType == 1 && node.childNodes && node.tagName.toUpperCase() != "SCRIPT" && node.tagName.toUpperCase != "STYLE") {
            for (var child = 0; child < node.childNodes.length; ++child) {
                child = child + searchWithinNode(node.childNodes[child], te, len);
            }
        }
        return skip;
    }
    searchWithinNode(document.body, text, text.length);
}