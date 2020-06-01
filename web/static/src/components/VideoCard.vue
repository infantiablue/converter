<template>
  <div class="card border-primary mb-3">
    <div class="youtube" :data-embed="videoid" :data-img="thumbnail"><div class="play-button"></div></div>
      <div class="card-body">
        <h6 class="card-title">{{title}}</h6>
        <div class="input-group mb-3"><input class="form-control w-75" :id="'link' + videoid" type="text" :value="'https://youtu.be/' + videoid" readonly>
        <div class="input-group-append">
          <button v-on:mouseleave="updateCopyText" v-on:click="copy_text ='Copied'"  title="Copied" data-container="body" data-toggle="popover" data-placement="top" data-original-title="" data-content="Copied" type="button" class="btn btn-primary btn-sm" data-clipboard-action="copy" :data-clipboard-target="'#link' + videoid" >{{copy_text}}</button>
        </div>
      </div>
    </div>
  </div>
</template>    
<script>
  module.exports = {
    data() {
      return {
        copy_text: 'Copy'
      }
    },
    props: ['title', 'thumbnail', 'videoid'],
    mounted: function(){       
    },
    methods: {
      updateCopyText: function() {
        if (this.copy_text === 'Copied'){
          this.copy_text = 'Copy'    
        }
      }
    },
    updated() {
    }
  }
</script>
<style>
.wrapper {
  max-width: 320px;
  margin: auto;
  padding: 0 20px;
}

.youtube {
  margin-bottom: 30px;
  position: relative;
  padding-top: 56.25%;
  overflow: hidden;
  cursor: pointer;
}
.youtube img {
  width: 100%;
  top: -0.1%;
  left: 0;
  opacity: 0.7;
}
.youtube .play-button {
  width: 90px;
  height: 60px;
  box-shadow: 0 0 30px rgba( 0,0,0,0.6 );
  z-index: 1;
  opacity: 0.8;
  border-radius: 6px;
}
.youtube .play-button:before {
  content: "";
  border-style: solid;
  border-width: 15px 0 15px 26.0px;
  border-color: transparent transparent transparent #fff;
}
.youtube img,
.youtube .play-button {
  cursor: pointer;
}
.youtube img,
.youtube iframe,
.youtube .play-button,
.youtube .play-button:before {
  position: absolute;
}
.youtube .play-button,
.youtube .play-button:before {
  top: 50%;
  left: 50%;
  transform: translate3d( -50%, -50%, 0 );
}
.youtube iframe {
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
}
</style>