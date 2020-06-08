'use strict'

function removeTag(cdoc, tagString) {

    let c = cdoc.getElementsByTagName(tagString);
    let len = c.length;
    let tElem;
    for (let dt = 0; dt < len; dt++) {
        tElem = c[len - dt - 1];
        // Do not delete iframes with links to youtube videos
        if ((tagString == "IFRAME") && (tElem.src.search(/youtube/) != -1)) {
            continue;
        }

        // Do not delete this element if it is either a H1 tag
        //(or contains child elements which are H1)
        let h1elems = tElem.getElementsByTagName("H1");
        if (tElem.nodeName == "H1" || h1elems.length > 0)
            continue;

        if (tElem.id == undefined || tElem.id.substr(0, 11) !== "tranquility") {
            tElem.parentNode.removeChild(tElem);
        }

    }
}

function deleteHiddenElements(cdoc, tagString) {
    // Remove elements that have display==none or visibility==hidden
    let elems = cdoc.getElementsByTagName(tagString);

    let ignoreList = ["HEAD", "TITLE"];

    for (let i = elems.length - 1; i >= 0; i--) {

        if (ignoreList.includes(elems[i].nodeName.toUpperCase())) {
            continue;
        }

        let cssProp = window.getComputedStyle(elems[i], null);
        let cssVisibility = cssProp.getPropertyValue("visibility");
        let cssDisplay = cssProp.getPropertyValue("display");

        if (((cssVisibility != undefined) && (cssVisibility == 'hidden')) ||
            ((cssDisplay != undefined) && (cssDisplay == 'none'))) {
            elems[i].parentNode.removeChild(elems[i]);
        }
    }
}

function deleteZeroSizeImages(cdoc) {
    let images = cdoc.getElementsByTagName('IMG');
    for (let i = images.length - 1; i >= 0; i--) {
        if (parseInt(images[i].getAttribute('height')) == 0 ||
            parseInt(images[i].getAttribute('width')) == 0) {
            images[i].parentNode.removeChild(images[i]);
        }
    }
}

function reformatHeader(cdoc) {

    let heads = cdoc.getElementsByTagName('HEAD');
    for (let i = 0; i < heads.length; i++) {
        let hChildren = heads[i].getElementsByTagName("*");
        let titleNodeCount = 0;
        while (hChildren.length > titleNodeCount) {
            if (hChildren[titleNodeCount].nodeName.toUpperCase() !== "TITLE") {
                heads[i].removeChild(hChildren[titleNodeCount]);
            } else {
                titleNodeCount++;
            }
        }
    }
}

function computeSize(dElem) {

    // Compute size removes spaces to do a better job of true size calculations
    //
    if (dElem.innerHTML) {
        if (dElem.textContent) {
            return dElem.textContent.replace(/\s/g, '').length;
        } else if (dElem.innerText) {
            return dElem.innerText.replace(/\s/g, '').length;
        } else {
            return 0;
        }
    } else {
        return 0;
    }
}

function pruneTag(cdoc, tagString, thresholdPctg, minSize, totalSize) {

    let c = cdoc.getElementsByTagName(tagString);
    let len = c.length;
    let tElem;
    for (let i = 0; i < len; i++) {
        tElem = c[len - i - 1];

        // If the DIV has a H1 child, then we want to retain the article
        // heading and not delete it.
        let h1elems = tElem.getElementsByTagName("H1");
        if (h1elems.length > 0)
            continue;

        let cLength = computeSize(tElem);
        let pctg = cLength / totalSize;
        // Experimental; do not delete if the text content is > threshold of innerHTML
        // currently hardcoded; trying to do better with blog style pages and comments
        let ilength = tElem.innerHTML.replace('/\s/g', '').length + 1;
        let inner_html_pctg = cLength / ilength;
        if (((inner_html_pctg < 0.5) && (pctg < thresholdPctg)) || (cLength <= minSize)) {
            tElem.parentNode.removeChild(tElem);
        } else {
            // Do nothing
        }
    }
}

function replaceParent(cdoc, tagString, thresholdPctg) {

    let c = cdoc.getElementsByTagName(tagString);
    let cArray = [];
    let len = c.length;
    for (let i = 0; i < len; i++) {
        cArray[i] = c[i];
    }
    cArray.sort(function (a, b) {
        return b.innerHTML.length - a.innerHTML.length
    });

    let tElem;
    for (let i = 0; i < len; i++) {
        tElem = cArray[len - i - 1];
        if ((tElem.parentNode != undefined) && (tElem.parentNode.tagName == tElem.tagName)) {
            let cLength = computeSize(tElem);
            let pLength = computeSize(tElem.parentNode);
            let pctg = cLength / pLength;
            if ((pctg > thresholdPctg)) {
                // If grandparent exists replace parent with this element
                // else, remove all siblings
                let grandparent = tElem.parentNode.parentNode;
                if (grandparent != undefined)
                    grandparent.replaceChild(tElem.cloneNode(true), tElem.parentNode);
                else {
                    let siblings = tElem.parentNode.childNodes;
                    for (let j = siblings.length - 1; j > -1; j--) {
                        if (siblings[j] !== tElem) {
                            tElem.parentNode.removeChild(siblings[j]);
                        }
                    }
                }
            } else {
            }
        }
    }
}

function removeWhiteSpaceComments(cdoc) {

    let cnodes = cdoc.childNodes;
    for (let i = cnodes.length - 1; i > -1; i--) {
        // Make sure that PRE nodes are ignored
        // Otherwise, their spaces and line breaks are removed
        // destroying their formatting

        if (cnodes[i].nodeName == "PRE") {
            continue;
        }
        if (cnodes[i].nodeType == 1) {
            removeWhiteSpaceComments(cnodes[i]);
        }
        if (cnodes[i].nodeType == 3) {
            let allText = cnodes[i].data;
            cnodes[i].data = allText.replace(/\s{2,}/g, ' ');
        }
        if (cnodes[i].nodeType == 8) {
            cnodes[i].parentNode.removeChild(cnodes[i]);
        }
    }
}

function pruneAdsTag(cdoc, url, tagString, thresholdPctg, totalSize, imgCollection) {

    let c = cdoc.getElementsByTagName(tagString);
    let len = c.length;
    let tElem;
    for (let i = 0; i < len; i++) {
        tElem = c[len - i - 1];

        // If the DIV has a H1 child, then we want to retain the article
        // heading and not delete it.
        let h1elems = tElem.getElementsByTagName("H1");
        if (h1elems.length > 0)
            continue;

        let cLength = computeSize(tElem);
        let pctg = cLength / totalSize;
        // If the DIV/SECTION/ARTICLE is empty remove it right away
        if (cLength == 0) {
            tElem.parentNode.removeChild(tElem);
        }
            // If the DIV does not contain a significant portion of the web content
            // AND the DIV contain mainly list elements then we can process to remove ads
            // Here, we use the "A" anchor node as a proxy for the LI node since each
            // navigation menu (or ads links menu) has a list of LI nodes that contain
            // anchor nodes with links to a new web page/section
        //
        else if (pctg < 0.8) {
            let anchorNodes = tElem.getElementsByTagName("A");
            let anchorLength = 0;
            let num_words = 0;
            for (let j = 0; j < anchorNodes.length; j++) {
                // Ignore links that are # tags in the same document
                // These are typically table of content type links for the
                // current document and are useful to retain
                //
                if (anchorNodes[j].href.split("#")[0] == url.split("#")[0])
                    continue;
                anchorLength += computeSize(anchorNodes[j]);
                num_words += anchorNodes[j].textContent.split(/\s+/).length;
            }
            let avg_words_per_anchor = num_words / anchorNodes.length;
            let inner_div_pctg = anchorLength / cLength;
            // If the DIV has > thresholdPctg of its content within anchor nodes
            // remove, the DIV.  Additionally we can also look at the number of words
            // per anchor, but for now, that is not enabled
            if (inner_div_pctg >= thresholdPctg) {
                let images = tElem.getElementsByTagName('img');
                if (images.length > 0) {
                    for (let k = 0; k < images.length; k++) {
                        if (images[k].src in imgCollection) {
                            delete imgCollection[images[k].src];
                        }
                    }
                }
                tElem.parentNode.removeChild(tElem);
            }
        } else {
            // Do nothing
        }
    }
}

function cloneImages(cdoc, collection) {

    // This function also preserves the original width/height of the images
    // in data fields
    let images = cdoc.getElementsByTagName('IMG');
    for (let i = 0; i < images.length; i++) {
        let img = new Image();
        img.src = images[i].src;
        img.setAttribute('data-dfsIndex', images[i].getAttribute('data-dfsIndex'));
        img.alt = images[i].alt;

        collection[images[i].src] = img;
        console.log(images[i].src + ": " + images[i].alt);
    }
}

function removeNodeRecursive(thisNode) {
    let thisNodeTextLen = computeSize(thisNode);
    let parent = thisNode.parentNode;
    let parentTextLen = computeSize(parent);
    if (parentTextLen == thisNodeTextLen) {
        removeNodeRecursive(parent);
    } else {
        parent.removeChild(thisNode);
    }
}

function processContentDoc(contentDoc, thisURL) {

    // Remove all script tags
    //
    let scriptTags = ["SCRIPT", "NOSCRIPT"];
    for (let i = 0; i < scriptTags.length; i++) {
        removeTag(contentDoc, scriptTags[i]);
    }

    // Now replace document.documentElement; It looks like we need this step for
    // the window.getComputedStyle() function to work correctly
    // we can then copy over the document to the contentDoc variable and continue
    // as before
    //
    document.replaceChild(contentDoc.documentElement, document.documentElement);
    contentDoc = document;

    // Delete All Hidden Elements before doing anything further
    // These could be hidden images, div, spans, spacers, etc...
    // Delete any content that has display = 'none' or visibility == 'hidden'
    // This was originally done only for spacer images, but seems like a meaningful thing
    // to do for all elements, given that all scripts are also deleted in the Tranquility view
    //
    deleteHiddenElements(contentDoc, "*");
    console.log("Removed Hidden elements");

    // Remove zero sized images; this is just another way of hiding elements
    // otherwise, these can get cloned and reappear
    // resized to the reading width, which is very annoying
    // This has a side effect of removing images that have not yet loaded
    // The problem will be addressed in a later release
    //
    deleteZeroSizeImages(contentDoc);
    console.log("Removed Zero Sized Images");

    // Remove any links that have an onclick event (these are usually for sharing to social media)
    // removing such links is consistent with our preference to delete all javascript
    //
    console.log("Removing links with associated javascript events...");
    let all_links = contentDoc.getElementsByTagName("A");
    for (let i = all_links.length - 1; i >= 0; i--) {
        let onclickVal = all_links[i].getAttribute('onclick');
        if (onclickVal != null) {
            removeNodeRecursive(all_links[i]);
        }
    }

    // If there is a single "ARTICLE" tag, then replace the entire document content with just the
    // contents of the article.  Trust that the content creator has done the correct thing
    //
    let articles = contentDoc.getElementsByTagName("article");
    if (articles.length == 1) {
        let docBody = contentDoc.body;
        let mainArticle = articles[0].cloneNode(true);
        while (docBody.firstChild) {
            docBody.removeChild(docBody.firstChild);
        }
        docBody.appendChild(mainArticle);
    }

    // Remove unnecessary whitespaces and comments
    removeWhiteSpaceComments(contentDoc);

    console.log("Removed white spaces and comments");

    // Cleanup the head and unnecessary tags
    let delTags = ["STYLE", "LINK", "META", "SCRIPT", "NOSCRIPT", "IFRAME",
        "SELECT", "DD", "INPUT", "TEXTAREA", "HEADER", "FOOTER",
        "NAV", "FORM", "BUTTON", "PICTURE", "FIGURE", "SVG"];
    for (let i = 0; i < delTags.length; i++) {
        removeTag(contentDoc, delTags[i]);
    }

    console.log("Cleaned up unnecessary tags and headers");

    // Reformat the header and use custom css
    reformatHeader(contentDoc);

    console.log("Reformatted headers...");

    // Clone all the image nodes for later insertion
    let imgCollection = {};
    cloneImages(contentDoc.body, imgCollection);

    // Ensure that we set a base element before we replace the
    // Processing for ads related DIV's; several websites seem to use LI elements
    // within the ads DIV's, or for navigation links which are not required in the
    // Tranquility view.  In this section, we try to delete DIV's that have at least
    // x% of the DIV content within LI tags
    let pruneAdsTagList = ["UL", "DIV", "ARTICLE", "SECTION"];
    let totalSize = computeSize(contentDoc.documentElement);
    for (let p = 0; p < pruneAdsTagList.length; p++) {
        pruneAdsTag(contentDoc, thisURL, pruneAdsTagList[p], 0.7, totalSize, imgCollection);
    }

    console.log("Pruned the AdsTag");


    // Cleanup select tags that have content length smaller than minSize
    // This helps clean up a number of junk DIV's before we get to real content
    // Can be made a parameter in later versions
    // First run with minSize ZERO
    // Removed TD and DD for now
    let pruneTagList = ["LI", "DIV", "OL", "UL", "FORM", "TABLE", "ARTICLE", "SECTION", "SPAN", "P"];
    let minSize = 0;
    totalSize = computeSize(contentDoc.documentElement);
    for (let p = 0; p < pruneTagList.length; p++) {
        pruneTag(contentDoc, pruneTagList[p], 0.0, minSize, totalSize);
    }
    // Next run with minsize 200 (for a reduced subset of the tags)
    // Removed TD, TABLE, and DD for now
    pruneTagList = ["FORM", "DIV", "ARTICLE", "SECTION"];
    minSize = 5;
    totalSize = computeSize(contentDoc.documentElement);
    for (let p = 0; p < pruneTagList.length; p++) {
        pruneTag(contentDoc, pruneTagList[p], 0.0, minSize, totalSize);
    }

    // Second pass
    // Remove any elements that have zero length textContent
    pruneTagList = ["LI", "DIV", "OL", "UL", "FORM", "TABLE", "ARTICLE", "SECTION", "SPAN", "P"];
    minSize = 0;
    totalSize = computeSize(contentDoc.documentElement);
    for (let p = 0; p < pruneTagList.length; p++) {
        pruneTag(contentDoc, pruneTagList[p], 0.0, minSize, totalSize);
    }

    console.log("Completed second pass pruning");

    // Try to remove unnecessary nested DIV's
    // They mess up the padding and margins; use only in moderate pruning
    // They mess up the padding and margins; use only in moderate pruning
    // if the threshold is < 0.99999
    for (let i = 0; i < 5; i++) {
        replaceParent(contentDoc, "DIV", 0.99999);
        replaceParent(contentDoc, "SPAN", 0.99999);
    }

    console.log("Completed Replace parent loops");

}
