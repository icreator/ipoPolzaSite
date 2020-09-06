// ==UserScript==
// @name roiUserJS
// @description Голосование для roi.ru
// @author Privater
// @license MIT
// @version 1.0
// @include https://www.roi.ru/*
// ==/UserScript==
// 

//загрузка jquery
function addJQuery(callback) {
    var script = document.createElement("script");
    script.setAttribute("src", "//ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js");
    script.addEventListener('load', function() {
        var script = document.createElement("script");
        script.textContent = "window.jQ=jQuery.noConflict(true);(" + callback.toString() + ")();";
        document.body.appendChild(script);
    }, false);
    document.body.appendChild(script);
}

// the guts of this userscript
function main() {

    //открытие нового окна для голосования
    var createVoteTab=function(url){
        window.open(url,"","width=100,height=100,resizable=no,scrollbars=no,menubar=no,toolbar=no,location=no,directories=no,status=no");
    }

    var createVoteButtons=function(){
        //создаем общие кнопки голосования
        jQ('<div style="margin-left: 600px;">' +
            '<input type="radio" name="vote" value="-1" class="vote_global"> <span style="color: red">Против</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
            '<input type="radio" name="vote" value="0" class="vote_global"> <span style="color: blue">Как все</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
            '<input type="radio" name="vote" value="1" class="vote_global"> <span style="color: green">За</span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
            '<input type="button" value="Голосовать" class="do_vote">' +
            '</div><br>').insertBefore('.petitionlist');
        //к каждой инициативе добавляем свои кнопки
        jQ('.petitionlist .item').each(function(i,el){
            jQ('<div style="position: relative;">' +
                '<div style="position: absolute; right: 15px;">' +
                '<span style="color: red">-' +
                '<input type="radio" name="vote_'+i+'" value="-1" class="vote"></span> ' +
                '<span style="color: blue">?' +
                '<input type="radio" name="vote_'+i+'" value="0" class="vote"> ' +
                '<span style="color: green">+' +
                '<input type="radio" name="vote_'+i+'" value="1" class="vote"> ' +
                '</div>' +
                '</div>').prependTo(el);
        });
        //обработчик нажатий на общие кнопки
        jQ('.vote_global').change(function(){
            var global_vote=jQ('.vote_global:checked').val();
            $('input.vote').removeAttr('checked');
            $('input.vote[value='+global_vote+']').attr('checked','checked');
        });
        //обработчик нажатия на кнопку Голосовать
        jQ('.do_vote').click(function(){
            var maxI;
            var wnd;
            jQ('.petitionlist .item').each(function(i,el){
                if(jQ(el).find('input.vote:checked').length>0)
                {
                    var vote=jQ(el).find('input.vote:checked').val();

                    //открываем новые окна с небольшой задержкой
                    setTimeout(function(){
                        window.open(jQ(el).find('.link a').attr('href')+'#vote='+vote,'_newtab'+i);
                    },i*2500);
                    maxI=i*2500;
                }
            });
            setTimeout(function(){
                w.location.reload();
            },maxI+5500);
            return false;
        });
    }
    //инициализируем объект window
    var w;
    if (typeof(unsafeWindow) != 'undefined') {
        w = unsafeWindow
    } else {
        w = window;
    }
    //если передана ссылка на голосование
    if (/www.roi.ru\/\d+\/#vote=(-1|0|1)/.test(w.location.href)) {
        m=w.location.href.match(/www.roi.ru\/\d+\/#vote=(-1|0|1)/);
        var voteAs=m[1];

        if(voteAs=='0')
        {
            m=jQ('#voting-status .affirmative .title span').text().match(/\((\d+)\s/);
            affirmative=parseInt(m[1]);
            m=jQ('#voting-status .negative .title span').text().match(/\((\d+)\s/);
            negative=parseInt(m[1]);
            if(negative>affirmative) voteAs='-1';
            else voteAs='1';
        }

        var clickEvent  = w.document.createEvent ('MouseEvents');
        clickEvent.initEvent ('click', true, true);

        //переопределяем функцию alert для блокирования всплывающего окна
        w.alert=function(){i=setInterval(function(){w.close() },2500);};

        // жмем кнопки
        if(voteAs=='1') jQ('#voting-status .affirmative a').get(0).dispatchEvent (clickEvent);
        else jQ('#voting-status .negative a').get(0).dispatchEvent (clickEvent);



    }
    //иначе ищем список инициатив и добавляем к ним кнопки
    else if(jQ('.petitionlist .item').length>0)
    {
        createVoteButtons();
    }
}

// загружаем локальную jquery для использования в скрипте
addJQuery(main);