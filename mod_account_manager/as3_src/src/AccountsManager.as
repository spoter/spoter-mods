package
{
	import flash.text.TextField;

	import net.wg.gui.components.controls.CheckBox;
	import net.wg.infrastructure.base.AbstractWindowView;
	import net.wg.gui.components.controls.SoundButton;
	import scaleform.clik.events.ButtonEvent;

	import flash.events.*;
	import flash.display.*;
	import flash.utils.*;
	import net.wg.gui.login.impl.views.SimpleForm;

	public class AccountsManager extends AbstractWindowView 
	{
		public var py_log					: Function;
		public var callFromFlash			: Function;
		public var py_getTranslate			: Function;
		public var py_setLoginDataById		: Function;
		public var py_openAddAccountWindow	: Function;

		private var langData	: Object;

		private var accountsList		: TextField;
		private var newAccButton		: SoundButton;
		private var autoEnterCheckBox	: CheckBox;
		private var _form				: SimpleForm;

		public function AccountsManager() 
		{
			super();
			this.isCentered	= true;
		}

		public function as_callToFlash(data_arr : Array) : void
		{
			try
			{
				var htmlText : String = "";

				for each (var data : Object in data_arr)
				{
					htmlText += "<font size='17' color='#FFFFFF'>" + data.user + "<br />" +
					"<img src='img://gui/maps/icons/library/BattleResultIcon-1.png'> " + data.cluster + "</font><br />" +
					"<a href='event:0_" + data.id + "'>" + this.langData.submit_l10n + "</a>    " +
					"<a href='event:1_" + data.id + "'>" + this.langData.edit_l10n + "</a>    " +
					"<a href='event:2_" + data.id + "'>" + this.langData.delete_l10n + "</a><br />" +
					"<img width='" + this.accountsList.width.toString() + "' src='img://gui/flash/AccountsManager/splitter.png'><br /><br />";
				}
				this.accountsList.htmlText = htmlText;
			} catch(err : Error)
			{
				this.py_log("as_callToFlash " + err.message);
			}
		}

		public function handleLinkClick(e : TextEvent) : void
		{
			var action	: String = e.text.charAt(0);
			var id		: String = e.text.substring(2);

			switch (e.text.charAt(0))
			{
				case "0":
					action = "submit";
					break;
				case "1":
					action = "edit";
					break;
				case "2":
					action = "delete";
					break;
			}

			if (action == "submit") {
				this.py_setLoginDataById(id, this._form);
				if (this.autoEnterCheckBox.selected) {
					this._form.submit.dispatchEvent(new ButtonEvent(ButtonEvent.CLICK));
				}
			} else {
				this.callFromFlash({
					"action"	: action,
					"id"		: id
				});
			}
		}

		public function handleAddButtonClick(e : ButtonEvent) : void
		{
			this.py_openAddAccountWindow();
		}

		override protected function onPopulate() : void
		{
			super.onPopulate();

			this._form = this.recursiveFindDOC(DisplayObjectContainer(stage), "LoginFormUI") as SimpleForm;

			this.langData = this.py_getTranslate();

			this.window.title = this.langData.window_title_l10n;
			this.width	= 340;
			this.height	= 530;

			try
			{
				this.accountsList				= new TextField();
				this.accountsList.x				= 10;
				this.accountsList.y				= 10;
				this.accountsList.width			= 320;
				this.accountsList.height		= 490;
				this.accountsList.multiline		= true;
				this.accountsList.selectable	= false;
				//this.accountsList.background	= true;
				//this.accountsList.border		= true;
				this.accountsList.htmlText		= "";
				this.addChild(this.accountsList);
				this.accountsList.addEventListener(TextEvent.LINK, this.handleLinkClick);

				this.newAccButton = this.addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
					label:	this.langData.add_l10n,
					width:	100,
					x:		122,
					y:		500
				})) as SoundButton;

				this.autoEnterCheckBox = this.addChild(App.utils.classFactory.getComponent("CheckBox", CheckBox, {
					label:		this.langData.auto_enter_l10n,
					x:			10,
					y:			500,
					selected:	true
				})) as CheckBox;

				this.newAccButton.addEventListener(ButtonEvent.CLICK, this.handleAddButtonClick);
			} catch (err : Error)
			{
				this.py_log("onPopulate " + err.message);
			}
		}

		private function recursiveFindDOC(dOC:DisplayObjectContainer, className:String) : DisplayObjectContainer {
			var child:DisplayObject = null;
			var childOC:DisplayObjectContainer = null;
			var i:int = 0;
			var result:DisplayObjectContainer = null;
			while (i < dOC.numChildren) {
				child = dOC.getChildAt(i);
				if ((child is DisplayObject) && (getQualifiedClassName(child) == className)) result = child as DisplayObjectContainer;
				if (result != null) return result;
				childOC = child as DisplayObjectContainer;
				if ((childOC) && (childOC.numChildren > 0)) result = this.recursiveFindDOC(childOC, className);
				i++;
			}
			return result;
		}

	}

}
