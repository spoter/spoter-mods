package oldskool.views.hangar
{
	import flash.display.Sprite;
	import net.wg.gui.lobby.hangar.ammunitionPanel.AmmunitionPanel;
    import scaleform.clik.events.ButtonEvent;
    import net.wg.gui.components.containers.MainViewContainer;
    import net.wg.infrastructure.base.AbstractView;
    import net.wg.infrastructure.events.LoaderEvent;
    import net.wg.infrastructure.interfaces.IManagedContent;
    import net.wg.infrastructure.interfaces.ISimpleManagedContainer;
    import net.wg.infrastructure.interfaces.IView;
    import net.wg.infrastructure.managers.impl.ContainerManagerBase;
    import net.wg.gui.lobby.hangar.Hangar;
	import flash.text.TextField;
	import flash.filters.DropShadowFilter;
	import flash.display.MovieClip;
	import flash.events.Event;
	import flash.events.MouseEvent;
	
    public class hangarMarks extends AbstractView
    {
		public var py_startPos:Function = null;
		public var py_newPos:Function = null;
		public var MOEContainer:Sprite = null;
		public var MoEText:TextField = null;
		public var MoEBackground:MovieClip = null;
		private var _dragging:Boolean = false;
		private var _draggingData:Array = null;
		private var _hangar:Hangar;	
		private var posX:int;
		private var posY:int;
		private var appWidht:Number = 1024;
		private var appHeight:Number = 768;
		
        override protected function onPopulate() : void
        {
		  
           super.onPopulate();
		   //App.instance.stage.addEventListener(Event.RESIZE, onResize);

		   
        }
      
        //private function onResize() : void
        //{
        //   this.appWidht = App.appWidth;
        //   this.appHeight = App.appHeight;
		//   
		//   this.MOEContainer.x = (this.appWidht + 220) / 2;	
		//   this.MOEContainer.y = 35;
		//   
        //}
		
		public function as_HideTankName() : void 
		{
			
			var ammunitionPanel:AmmunitionPanel = _hangar.ammunitionPanel as AmmunitionPanel;
			if (ammunitionPanel.vehicleStateMsg.parent)
			{
				ammunitionPanel.vehicleStateMsg.parent.removeChild(ammunitionPanel.vehicleStateMsg);
			}
		}

		public function as_setText(param1:String) : void
		{
			var htmlData:String = param1;
			try
			{
				this.MoEText.htmlText = htmlData;
				this.MoEBackground.width = this.MoEText.width;
				this.MoEBackground.height = this.MoEText.height;

				return;
			}
			catch(e:Error)
			{
				DebugUtils.LOG_ERROR("[ERROR] HangarMOE: ",e.name);
				DebugUtils.LOG_ERROR(e.getStackTrace().toString());
				return;
			}
		}

		public function as_setPosition(param1:Number, param2:Number) : void
		{
			var _x:Number = param1;
			var _y:Number = param2;
			try
			{
				
				this.MOEContainer.x = _x;	
				this.MOEContainer.y = _y;
				
				return;
			}
			catch(e:Error)
			{
				DebugUtils.LOG_ERROR("[ERROR] HangarMOE: ",e.name);
				DebugUtils.LOG_ERROR(e.getStackTrace().toString());
				return;
			}
		}	  

		public function as_setBackground(param1:Boolean, param2:Number, param3:Number) : void
		{
			var bgenabled:Boolean = param1;
			var bgcolor:Number = param2;
			var bgalpha:Number = param3;
			
			try
			{
				this.MoEBackground.visible = bgenabled;
				this.MoEBackground.graphics.clear();
				this.MoEBackground.graphics.beginFill(Number(bgcolor), Number(bgalpha));
				this.MoEBackground.graphics.drawRect(0, 0, 100, 100);
				this.MoEBackground.graphics.endFill();

				return;
			}
			catch(e:Error)
			{
				DebugUtils.LOG_ERROR("[ERROR] HangarMOE: ",e.name);
				DebugUtils.LOG_ERROR(e.getStackTrace().toString());
				return;
			}
		}	 
	  
        override protected function configUI() : void
        {
            super.configUI();
           
            var containerMgr:ContainerManagerBase = App.containerMgr as ContainerManagerBase;
            containerMgr.loader.addEventListener(LoaderEvent.VIEW_LOADED, onViewLoaded);
           
            for each (var container:ISimpleManagedContainer in containerMgr.containersMap)
            {
                var viewContainer:MainViewContainer = container as MainViewContainer;
                if (viewContainer != null)
                {
                    var num:int = viewContainer.numChildren;
                    for (var idx:int = 0; idx < num; ++idx)
                    {
                        var view:IView = viewContainer.getChildAt(idx) as IView;
                        if (view != null)
                        {
                            processView(view);
                        }
                    }
                    var topmostView:IManagedContent = viewContainer.getTopmostView();
                    if (topmostView != null)
                    {
                        viewContainer.setFocusedView(topmostView);
                    }
                }
            }
        }
       
        override protected function onDispose() : void
        {
            var containerMgr:ContainerManagerBase = App.containerMgr as ContainerManagerBase;
            containerMgr.loader.removeEventListener(LoaderEvent.VIEW_LOADED, onViewLoaded);
           
            super.onDispose();
        }
       
        private function onViewLoaded(event:LoaderEvent) : void
        {
            processView(event.view as IView);
        }
 
        private function processView(view:IView) : void
        {
			
            if (view.as_config.alias == 'hangar')
            {  
				_hangar = view as Hangar;
                
				var filter:DropShadowFilter = null;
				
				
				this.MoEText = new TextField();
				this.MoEText.autoSize = "left";
				this.MoEText.htmlText = "";
				this.MoEText.multiline = true;
				this.MoEText.wordWrap = true;
				this.MoEText.width = 400;
				this.MoEText.height = 150;
				this.MoEText.selectable = false;
				filter = new DropShadowFilter();
				filter.distance = 0;
				filter.angle = 90;
				filter.color = Number(0);
				filter.alpha = 100;
				filter.blurX = filter.blurY = 5;
				filter.strength = 3;
				filter.quality = 3;
				filter.inner = false;
				filter.knockout = false;
				this.MoEText.filters = [filter];
				
				this.MoEBackground = new MovieClip();
                this.MoEBackground.visible = true;
                this.MoEBackground.width = this.MoEText.width;
                this.MoEBackground.height = this.MoEText.height;
                this.MoEBackground.graphics.clear();
                this.MoEBackground.graphics.beginFill(0x000000, 0.0);
                this.MoEBackground.graphics.moveTo(0,0);
                this.MoEBackground.graphics.lineTo(100,0);
                this.MoEBackground.graphics.lineTo(100,100);
                this.MoEBackground.graphics.lineTo(0,100);
                this.MoEBackground.graphics.lineTo(0,0);
                this.MoEBackground.graphics.endFill();
				this.MoEBackground.visible = false;
				
				this.MOEContainer = new Sprite();	
				this.MOEContainer.addChild(MoEBackground);
				this.MOEContainer.addChild(MoEText);
				this.MOEContainer.x = (App.appWidth + 400) / 2;	
				this.MOEContainer.y = 35;
				this.posX = int(this.MOEContainer.x - (App.appWidth / 2.0));
				this.posY = int(this.MOEContainer.y - (App.appHeight / 2.0));
				
				this.MOEContainer.addEventListener(MouseEvent.MOUSE_DOWN, handleMouseDown);
				this.MOEContainer.addEventListener(MouseEvent.MOUSE_UP, handleMouseUp);
				this.MOEContainer.addEventListener(MouseEvent.MOUSE_MOVE, handleMouseMove);

				view.addChild(this.MOEContainer);

            }
        }
		
		
		private function handleMouseDown(event:MouseEvent) : void 
		{
			_dragging = true;
			_draggingData = [int(this.MOEContainer.x), int(this.MOEContainer.y)];
			this.MOEContainer.startDrag();
		}
		
		private function handleMouseMove(event:MouseEvent) : void 
		{
			if (_dragging) 
			{
			}
		}
		
		private function handleMouseUp(event:MouseEvent) : void 
		{
			if (_dragging) 
			{
				_dragging = false;
				this.MOEContainer.stopDrag();
				
				this.posX = int(this.MOEContainer.x - (App.appWidth / 2.0));
				this.posY = int(this.MOEContainer.y - (App.appHeight / 2.0));
				this.py_newPos(this.MOEContainer.x, this.MOEContainer.y);
				
			}
		}
		
    }
}