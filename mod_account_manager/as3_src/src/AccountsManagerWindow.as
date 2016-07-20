package
{
	import net.wg.infrastructure.base.AbstractWindowView;
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.gui.components.controls.TextFieldShort;
	import net.wg.gui.components.controls.TextInput;
	import net.wg.gui.components.controls.CheckBox;
	import net.wg.gui.components.controls.DropdownMenu;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.data.DataProvider;

	public class AccountsManagerWindow extends AbstractWindowView 
	{
		public var py_log				: Function;
		public var py_get_clusters		: Function;
		public var py_getTranslate		: Function;
		public var py_setAddAccount		: Function;
		public var py_setEditAccount	: Function;

		private var wmode			: String = "add";
		private var langData		: Object;
		private var submitBtn		: SoundButton;
		private var cancelBtn		: SoundButton;
		private var showPswd		: CheckBox;
		private var titleLabel		: TextFieldShort;
		private var emailLabel		: TextFieldShort;
		private var passwordLabel	: TextFieldShort;
		private var clusterLabel	: TextFieldShort;
		private var titleVal		: TextInput;
		private var loginVal		: TextInput;
		private var passwordVal		: TextInput;
		private var clusterVal		: DropdownMenu;
		private var qweid			: String;

		public function AccountsManagerWindow() 
		{
			super();
			this.isModal	= true;
			this.canClose	= true;
			this.isCentered	= true;
		}

		private function handleSubmitBtnClick(e : ButtonEvent) : void
		{
			if (this.titleVal.text == "") {
				this.titleVal.highlight = true;
				return;
			}
			if (this.isValidEmail(this.loginVal.text) == false) {
				this.loginVal.highlight = true;
				return;
			}
			if (this.wmode == "add") {
				this.py_setAddAccount(this.titleVal.text, this.loginVal.text, this.passwordVal.text, this.clusterVal.selectedIndex);
			} else if (this.wmode == "edit") {
				this.py_setEditAccount(this.qweid, this.titleVal.text, this.loginVal.text, this.passwordVal.text, this.clusterVal.selectedIndex);
			}
		}

		private function handleCancelBtnClick(e : ButtonEvent) : void
		{
			this.onWindowClose();
		}

		private function handleShowPswdClick(e : ButtonEvent) : void
		{
			this.passwordVal.displayAsPassword = !this.passwordVal.displayAsPassword;
		}

		public function as_setEditAccountData(id : String, title : String, email : String, password : String, cluster : int) : void
		{
			this.qweid = id;
			this.titleVal.text = title;
			this.loginVal.text = email;
			this.passwordVal.text = password;
			this.clusterVal.selectedIndex = cluster;
			this.wmode = "edit";
		}

		public function as_setAddAccount() : void
		{
			this.wmode = "add";
		}

		override protected function onPopulate() : void
		{
			super.onPopulate();

			this.langData	= this.py_getTranslate();

			this.window.title = this.langData.window_title_l10n;
			this.window.setTitleIcon("team");
			this.width	= 340;
			this.height	= 200;

			try
			{
				// Nickname
				this.titleLabel = this.addChild(App.utils.classFactory.getComponent("TextFieldShort", TextFieldShort, {
					label: this.langData.nick_l10n,
					selectable: false,
					showToolTip: false,
					x: 5,
					y: 10
				})) as TextFieldShort;

				this.titleVal = this.addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
					width: 210,
					x: 60,
					y: 5
				})) as TextInput;

				// Email
				this.emailLabel = this.addChild(App.utils.classFactory.getComponent("TextFieldShort", TextFieldShort, {
					label: "Email:",
					selectable: false,
					showToolTip: false,
					x: 5,
					y: 40
				})) as TextFieldShort;

				this.loginVal = this.addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
					width: 210,
					x: 60,
					y: 35
				})) as TextInput;

				// Password
				this.passwordLabel = this.addChild(App.utils.classFactory.getComponent("TextFieldShort", TextFieldShort, {
					label: this.langData.password_l10n,
					selectable: false,
					showToolTip: false,
					x: 5,
					y: 70
				})) as TextFieldShort;

				this.passwordVal = this.addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
					displayAsPassword: true,
					width: 210,
					x: 60,
					y: 65
				})) as TextInput;

				// Show password
				this.showPswd = this.addChild(App.utils.classFactory.getComponent("CheckBox", CheckBox, {
					label: this.langData.show_password_l10n,
					visible: true,
					x: 60,
					y: 95
				})) as CheckBox;
				this.showPswd.addEventListener(ButtonEvent.CLICK, this.handleShowPswdClick);

				// Cluster
				this.clusterLabel = this.addChild(App.utils.classFactory.getComponent("TextFieldShort", TextFieldShort, {
					label: this.langData.server_l10n,
					selectable: false,
					showToolTip: false,
					x: 5,
					y: 125
				})) as TextFieldShort;

				var dp : Array = this.py_get_clusters();
				this.clusterVal = this.addChild(App.utils.classFactory.getComponent("DropdownMenu", DropdownMenu, {
					rowCount: 10,
					width: 210,
					x: 60,
					y: 120,
					menuDirection: "down",
					itemRenderer: "DropDownListItemRendererSound",
					dropdown: "DropdownMenu_ScrollingList",
					dataProvider: new DataProvider(dp),
					selectedIndex: 0
				})) as DropdownMenu;

				this.submitBtn = this.addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
					label: this.langData.save_l10n,
					width: 100,
					x: 120,
					y: 165
				})) as SoundButton;
				this.submitBtn.addEventListener(ButtonEvent.CLICK, this.handleSubmitBtnClick);

				this.cancelBtn = this.addChild(App.utils.classFactory.getComponent("ButtonBlack", SoundButton, {
					label: this.langData.cancel_l10n,
					width: 100,
					x: 230,
					y: 165
				})) as SoundButton;
				this.cancelBtn.addEventListener(ButtonEvent.CLICK, this.handleCancelBtnClick);
			} catch (err : Error)
			{
				this.py_log("onPopulate " + err.getStackTrace());
			}
		}

		private function isValidEmail(email : String) : Boolean
		{
			var emailExpression : RegExp = /([a-z0-9._-]+?)@([a-z0-9.-]+)\.([a-z]{2,4})/;
			return emailExpression.test(email);
		}

	}

}
