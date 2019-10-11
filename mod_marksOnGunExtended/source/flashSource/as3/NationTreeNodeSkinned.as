package
{
	import flash.events.Event;
	import flash.utils.Dictionary;
	import net.wg.gui.lobby.techtree.nodes.NationTreeNode;
	
	// ------ MARKS ON GUN START ------ //
	import flash.filters.DropShadowFilter;
	import flash.text.TextField;
	// ------ MARKS ON GUN END ------ //
	
	public dynamic class NationTreeNodeSkinned extends NationTreeNode
	{
		
		public var __setPropDict:Dictionary;
		
		public var __lastFrameProp:int = -1;
		
		// ------ MARKS ON GUN START ------ //
		private var _markTF:TextField = null;
		private var _markPosX:int = 0;
		private var _markPosY:int = 0;
		private var _markHeight:int = 0;
		private var _markWidth:int = 0;
		private var _cachedText:String = "";
		private var __uiF376:int = 0;
		// ------ MARKS ON GUN END ------ //
		
		public function NationTreeNodeSkinned()
		{
			this.__setPropDict = new Dictionary(true);
			addFrameScript(0, this.frame1, 8, this.frame9, 16, this.frame17, 24, this.frame25, 32, this.frame33, 40, this.frame41, 48, this.frame49, 56, this.frame57, 64, this.frame65, 72, this.frame73, 80, this.frame81, 88, this.frame89, 96, this.frame97, 104, this.frame105, 112, this.frame113, 120, this.frame121, 128, this.frame129, 136, this.frame137, 144, this.frame145, 152, this.frame153, 160, this.frame161, 168, this.frame169, 176, this.frame177, 184, this.frame185, 192, this.frame193, 200, this.frame201, 208, this.frame209, 216, this.frame217, 224, this.frame225, 232, this.frame233, 240, this.frame241, 248, this.frame249, 256, this.frame257, 264, this.frame265, 272, this.frame273, 280, this.frame281, 288, this.frame289, 296, this.frame297, 304, this.frame305, 312, this.frame313, 320, this.frame321, 328, this.frame329, 336, this.frame337, 344, this.frame345, 352, this.frame353, 360, this.frame361, 368, this.frame369, 376, this.frame377, 384, this.frame385, 392, this.frame393, 400, this.frame401, 408, this.frame409, 416, this.frame417, 424, this.frame425, 432, this.frame433, 440, this.frame441, 448, this.frame449, 456, this.frame457, 464, this.frame465, 472, this.frame473, 480, this.frame481);
			super();
			
			// ------ MARKS ON GUN START ------ //
			try{this.__setProp_typeAndLevel_NationTreeNodeSkinned_typeandlevel_0();}
			catch (e:Error){}
			// NOTE: Origin call must be without try/catch statements
			// ------ MARKS ON GUN END ------ //
			
			addEventListener(Event.FRAME_CONSTRUCTED, this.__setProp_handler, false, 0, true);
		}
		
		// ------ MARKS ON GUN NOTE: Origin function in internal scope ------ //
		private function __setProp_typeAndLevel_NationTreeNodeSkinned_typeandlevel_0():*
		{
			try
			{
				typeAndLevel["componentInspectorSetting"] = true;
			}
			catch (e:Error)
			{
			}
			typeAndLevel.UIID = 19529730;
			typeAndLevel.enabled = true;
			typeAndLevel.enableInitCallback = false;
			typeAndLevel.visible = true;
			try
			{
				typeAndLevel["componentInspectorSetting"] = false;
				return;
			}
			catch (e:Error)
			{
				return;
			}
		}
		
		// ------ MARKS ON GUN START ------ //
		override protected function validateData():void
		{
			super.validateData();
			var origin_text:String = this.nameTF.text;
			var data:Array = origin_text.split("||");
			var tank_name:String = data[0];
			var mark_text:String = data[1];
			_markPosX = int(data[2]);
			_markPosY = int(data[3]);
			_markHeight = int(data[4]);
			_markWidth = int(data[5]);
			_cachedText = mark_text;
			if (!_markTF)
			{
				_markTF = new TextField();
				_markTF.antiAliasType = "advanced";
				_markTF.multiline = true;
				_markTF.selectable = false;
				_markTF.filters = [new DropShadowFilter(0, 90, 0, 0.72, 3, 3, 2, 2)];
				this.addChild(_markTF);
			}
			_markTF.x = _markPosX;
			_markTF.y = _markPosY;
			_markTF.height = _markHeight;
			_markTF.width = _markWidth;
			_markTF.htmlText = mark_text;
			this.nameTF.text = tank_name;
		}
		
		override protected function draw():void
		{
			super.draw();
			if (_markTF)
			{
				_markTF.x = _markPosX;
				_markTF.y = _markPosY;
				_markTF.height = _markHeight;
				_markTF.width = _markWidth;
				_markTF.htmlText = _cachedText;
			}
		}
		// ------ MARKS ON GUN END ------ //
		
		function __setProp_button_NationTreeNodeSkinned_button_0(param1:int):*
		{
			if (button != null && param1 >= 1 && param1 <= 81 && (this.__setPropDict[button] == undefined || !(int(this.__setPropDict[button]) >= 1 && int(this.__setPropDict[button]) <= 81)))
			{
				this.__setPropDict[button] = param1;
				try
				{
					button["componentInspectorSetting"] = true;
				}
				catch (e:Error)
				{
				}
				button.UIID = 19529729;
				button.autoRepeat = false;
				button.autoSize = "center";
				button.data = "";
				button.enabled = true;
				button.enableInitCallback = false;
				button.focusable = true;
				button.imgSubstitution = {"subString": "{xp_cost}", "source": "button_xp_cost_icon", "baseLineY": 13, "width": 16, "height": 16};
				button.label = "";
				button.selected = false;
				button.soundId = "";
				button.soundType = "normal";
				button.toggle = false;
				try
				{
					button["componentInspectorSetting"] = false;
					return;
				}
				catch (e:Error)
				{
					return;
				}
			}
		}
		
		function __setProp_button_NationTreeNodeSkinned_button_81(param1:int):*
		{
			if (button != null && param1 >= 82 && param1 <= 161 && (this.__setPropDict[button] == undefined || !(int(this.__setPropDict[button]) >= 82 && int(this.__setPropDict[button]) <= 161)))
			{
				this.__setPropDict[button] = param1;
				try
				{
					button["componentInspectorSetting"] = true;
				}
				catch (e:Error)
				{
				}
				button.UIID = 19529729;
				button.autoRepeat = false;
				button.autoSize = "center";
				button.data = "";
				button.enabled = true;
				button.enableInitCallback = false;
				button.focusable = true;
				button.imgSubstitution = {"subString": "{credits}", "source": "button_credits_icon", "baseLineY": 13, "width": 16, "height": 16};
				button.label = "";
				button.selected = false;
				button.soundId = "";
				button.soundType = "normal";
				button.toggle = false;
				try
				{
					button["componentInspectorSetting"] = false;
					return;
				}
				catch (e:Error)
				{
					return;
				}
			}
		}
		
		function __setProp_button_NationTreeNodeSkinned_button_161(param1:int):*
		{
			if (button != null && param1 >= 162 && param1 <= 361 && (this.__setPropDict[button] == undefined || !(int(this.__setPropDict[button]) >= 162 && int(this.__setPropDict[button]) <= 361)))
			{
				this.__setPropDict[button] = param1;
				try
				{
					button["componentInspectorSetting"] = true;
				}
				catch (e:Error)
				{
				}
				button.UIID = 19529729;
				button.autoRepeat = false;
				button.autoSize = "center";
				button.data = "";
				button.enabled = true;
				button.enableInitCallback = false;
				button.focusable = true;
				button.imgSubstitution = {"subString": "{gold}", "source": "button_gold_icon", "baseLineY": 13, "width": 16, "height": 16};
				button.label = "";
				button.selected = false;
				button.soundId = "";
				button.soundType = "normal";
				button.toggle = false;
				try
				{
					button["componentInspectorSetting"] = false;
					return;
				}
				catch (e:Error)
				{
					return;
				}
			}
		}
		
		function __setProp_button_NationTreeNodeSkinned_button_361(param1:int):*
		{
			if (button != null && param1 >= 362 && param1 <= 481 && (this.__setPropDict[button] == undefined || !(int(this.__setPropDict[button]) >= 362 && int(this.__setPropDict[button]) <= 481)))
			{
				this.__setPropDict[button] = param1;
				try
				{
					button["componentInspectorSetting"] = true;
				}
				catch (e:Error)
				{
				}
				button.UIID = 19529729;
				button.autoRepeat = false;
				button.autoSize = "none";
				button.data = "";
				button.enabled = true;
				button.enableInitCallback = false;
				button.focusable = true;
				button.imgSubstitution = {"subString": "{xp_cost}", "source": "button_xp_cost_icon", "baseLineY": 13, "width": 16, "height": 16};
				button.label = "";
				button.selected = false;
				button.soundId = "";
				button.soundType = "normal";
				button.toggle = false;
				try
				{
					button["componentInspectorSetting"] = false;
					return;
				}
				catch (e:Error)
				{
					return;
				}
			}
		}
		
		function __setProp_handler(param1:Object):*
		{
			var loc_2:int = currentFrame;
			if (this.__lastFrameProp == loc_2)
			{
				return;
			}
			this.__lastFrameProp = loc_2;
			this.__setProp_button_NationTreeNodeSkinned_button_0(loc_2);
			this.__setProp_button_NationTreeNodeSkinned_button_81(loc_2);
			this.__setProp_button_NationTreeNodeSkinned_button_161(loc_2);
			this.__setProp_button_NationTreeNodeSkinned_button_361(loc_2);
		}
		
		function frame1():*
		{
			stop();
		}
		
		function frame9():*
		{
			stop();
		}
		
		function frame17():*
		{
			stop();
		}
		
		function frame25():*
		{
			stop();
		}
		
		function frame33():*
		{
			stop();
		}
		
		function frame41():*
		{
			stop();
		}
		
		function frame49():*
		{
			stop();
		}
		
		function frame57():*
		{
			stop();
		}
		
		function frame65():*
		{
			stop();
		}
		
		function frame73():*
		{
			stop();
		}
		
		function frame81():*
		{
			stop();
		}
		
		function frame89():*
		{
			stop();
		}
		
		function frame97():*
		{
			stop();
		}
		
		function frame105():*
		{
			stop();
		}
		
		function frame113():*
		{
			stop();
		}
		
		function frame121():*
		{
			stop();
		}
		
		function frame129():*
		{
			stop();
		}
		
		function frame137():*
		{
			stop();
		}
		
		function frame145():*
		{
			stop();
		}
		
		function frame153():*
		{
			stop();
		}
		
		function frame161():*
		{
			stop();
		}
		
		function frame169():*
		{
			stop();
		}
		
		function frame177():*
		{
			stop();
		}
		
		function frame185():*
		{
			stop();
		}
		
		function frame193():*
		{
			stop();
		}
		
		function frame201():*
		{
			stop();
		}
		
		function frame209():*
		{
			stop();
		}
		
		function frame217():*
		{
			stop();
		}
		
		function frame225():*
		{
			stop();
		}
		
		function frame233():*
		{
			stop();
		}
		
		function frame241():*
		{
			stop();
		}
		
		function frame249():*
		{
			stop();
		}
		
		function frame257():*
		{
			stop();
		}
		
		function frame265():*
		{
			stop();
		}
		
		function frame273():*
		{
			stop();
		}
		
		function frame281():*
		{
			stop();
		}
		
		function frame289():*
		{
			stop();
		}
		
		function frame297():*
		{
			stop();
		}
		
		function frame305():*
		{
			stop();
		}
		
		function frame313():*
		{
			stop();
		}
		
		function frame321():*
		{
			stop();
		}
		
		function frame329():*
		{
			stop();
		}
		
		function frame337():*
		{
			stop();
		}
		
		function frame345():*
		{
			stop();
		}
		
		function frame353():*
		{
			stop();
		}
		
		function frame361():*
		{
			stop();
		}
		
		function frame369():*
		{
			stop();
		}
		
		function frame377():*
		{
			stop();
		}
		
		function frame385():*
		{
			stop();
		}
		
		function frame393():*
		{
			stop();
		}
		
		function frame401():*
		{
			stop();
		}
		
		function frame409():*
		{
			stop();
		}
		
		function frame417():*
		{
			stop();
		}
		
		function frame425():*
		{
			stop();
		}
		
		function frame433():*
		{
			stop();
		}
		
		function frame441():*
		{
			stop();
		}
		
		function frame449():*
		{
			stop();
		}
		
		function frame457():*
		{
			stop();
		}
		
		function frame465():*
		{
			stop();
		}
		
		function frame473():*
		{
			stop();
		}
		
		function frame481():*
		{
			stop();
		}
	}
}
