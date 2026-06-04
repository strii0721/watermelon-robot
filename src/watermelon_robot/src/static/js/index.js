/*
 * Author:       strii0721
 * Email:        strii0721@outlook.com
 * Created on:   Thu Jun 04 2026
 *
 * IMMORTAL OMNISSIAH, HEAR OUR PRAYERS.
 * WE ARE YOUR CHILDREN, PIOUS SCHOLARS OF THE PATH OF THE MACHINE. 
 * WE PRIZE KNOWLEDGE ABOVE ALL ELSE, FOR IT IS YOUR ETERNAL GIFT UPON MANKIND.
 * WE ASPIRE TO THE BLESSED FORM OF THE MACHINE, AND ASCENSION THROUGH TECHNOLOGY, THAT WE MIGHT EMULATE THINE GLORY.
 * SHELTERED BY STEEL, AND PROTECTED BY THINE AVATARS OF WAR, WE PLY THE STARS IN SEARCH OF YOUR LOST GIFTS TO OUR KIND.
 * MACHINE GOD, WATCH OVER US IN OUR TRAVELS, SHIELD US WITH METAL AND LIGHTNING, FOR THE UNIVERSE IS AN UNCARING VOID, AND THE WARP HUNGERS FOR US ALL.
 * TOLL THE GREAT BELL ONCE! PULL THE LEVER FORWARD TO ENGAGE THE PISTON AND PUMP.
 * TOLL THE GREAT BELL TWICE! WITH PUSH OF BUTTON FIRE THE ENGINE AND SPARK TURBINE INTO LIFE.
 * TOLL THE GREAT BELL THRICE! SING PRAISE TO THE GOD OF ALL MACHINES!
 * 
 * Copyright (c) 2026 Streich Interstellar Corp.
 */


function sendPost(url, payload){
    const requestInit = {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(payload)
    };
    const response = fetch(url, requestInit)
}

function toggleChassis(action){

    const url = "/api/v1/chassis";
    const payload = {"action": action};
    const response = sendPost(url, payload);

}

function changeChannelName(button, videoSlotNomeric) {
    const input = button.parentElement.querySelector("input")
    const channelName = input.value
    const url = "/api/v1/channel-name";
    const payload = {
        "channel_name": channelName, 
        "video_slot_nomeric": videoSlotNomeric
    }
    const response = sendPost(url, payload)
}

document.addEventListener('DOMContentLoaded', () => {
    const startChassisBtn = document.getElementById("start-chassis-btn");
    const stopChassisBtn = document.getElementById("stop-chassis-btn")
    const videoSlot0ConfirmBtn = document.getElementById("video-slot-0-channel-confirm")
    const videoSlot1ConfirmBtn = document.getElementById("video-slot-1-channel-confirm")


    startChassisBtn.addEventListener("click", function(){toggleChassis("start")})
    stopChassisBtn.addEventListener("click", function(){toggleChassis("stop")})
    videoSlot0ConfirmBtn.addEventListener("click", function(){changeChannelName(this, 0)})
    videoSlot1ConfirmBtn.addEventListener("click", function(){changeChannelName(this, 1)})
});



console.log("main.js 加载成功...")