import { useState, useEffect } from "react";
import { Button, Layout, Menu, List, Typography, Modal } from "antd";
import axios from "axios";
import "./App.css";
import Login from "./Login";

const { Header, Content, Footer } = Layout;
const { Title, Paragraph } = Typography;

function App() {
	const [events, setEvents] = useState([]);
	const [isLoginModalVisible, setIsLoginModalVisible] = useState(false);
	const [, setActiveKey] = useState("1"); // Default key

	useEffect(() => {
		// Fetch events from the server
		axios
			.get("http://localhost:5001/events")
			.then((response) => setEvents(response.data))
			.catch((error) => console.error("Error fetching events:", error));
	}, []);

	const createEvent = () => {
		axios
			.post("http://localhost:5001/events", {
				name: `Event ${events.length + 1}`,
			})
			.then((response) => setEvents([...events, response.data]))
			.catch((error) => console.error("Error creating event:", error));
	};

	const showLoginModal = () => {
		setIsLoginModalVisible(true);
	};

	const handleLoginCancel = () => {
		setIsLoginModalVisible(false);
	};

	return (
		<Layout className="layout">
			<Header>
				<div className="logo">SparkBytes</div>
				<Menu
					theme="dark"
					mode="horizontal"
					defaultSelectedKeys={["1"]}
					onClick={({ key }) => setActiveKey(key)}
					className="navbar"
				>
					<div className="menu-left">
						<Menu.Item key="1">
							<a href="#home-page">Home Page</a>
						</Menu.Item>
						<Menu.Item key="2">
							<a href="#about-us">About Us</a>
						</Menu.Item>
						<Menu.Item key="3">
							<a href="#contact-us">Contact Us</a>
						</Menu.Item>
					</div>
					<div>
						<Menu.Item key="5">
							<Button type="primary">
								<a href="#sign-up">Sign Up</a>
							</Button>
						</Menu.Item>
						<Menu.Item key="4">
							<Button type="primary" onClick={showLoginModal}>
								Login
							</Button>
						</Menu.Item>
					</div>
				</Menu>
			</Header>

			<Content style={{ padding: "50px", backgroundColor: "#f0f2f5" }}>
				<div className="site-layout-content">
					<Title level={2}>Welcome to SparkBytes!</Title>
					<Paragraph>
						Reduce food waste at Boston University by sharing event details with
						excess food.
					</Paragraph>
					<section id="events">
						<Title level={3}>Upcoming Events</Title>
						<Paragraph>Total Events Listed: {events.length}</Paragraph>
						<Button
							type="primary"
							onClick={createEvent}
							style={{ marginBottom: "20px" }}
						>
							Create Event
						</Button>
						<List
							bordered
							dataSource={events}
							renderItem={(item) => (
								<List.Item key={item._id}>{item.name}</List.Item>
							)}
						/>
					</section>
				</div>
			</Content>
			<Footer style={{ textAlign: "center" }}>
				&copy; 2024 SparkBytes. All Rights Reserved.
			</Footer>
			<Modal
				title="Login"
				visible={isLoginModalVisible}
				onCancel={handleLoginCancel}
				footer={null}
			>
				<Login onCancel={handleLoginCancel} />
			</Modal>
		</Layout>
	);
}

export default App;
